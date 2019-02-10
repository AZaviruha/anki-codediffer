import re
import os

from aqt import mw
from anki.hooks import addHook, runHook
from anki.utils import stripHTML
from aqt.utils import showInfo
from aqt.qt import *
from aqt.reviewer import Reviewer

QUESTION = 'reviewQuestion'
ANSWER = 'reviewAnswer'
DIFF_QUEST_PATTERN = r'\[diff\].*\[/diff\]'
DIFF_ANSW_PATTERN = r'\[diff-answ\](.*)\[/diff-answ\]'

EVENT_CHANGED = 'CUSTOM::answerChanged'
EDITOR_ELEM_ID = 'codeEditor'
DIFFER_ELEM_ID = 'codeDiffer'

SUPPORTED_LANGUAGES = [
    'javascript',
    'python',
    'sql',
    'typescript'
]

SUPPORTED_THEMES = [
    'chrome',
    'monokai',
    'solarized_dark',
    'solarized_light'
]

# ====================== #
# Utils                  #
# ====================== #

def local(path):
    current = os.path.dirname(os.path.abspath(__file__))
    return f'{current}/{path}'

def bundledScript(name):
    content = open(local(f'js/{name}.js'), 'r', encoding='utf-8').read()
    return f'<script type="text/javascript">{content}</script>'

def bundledVendorScript(name):
    return bundledScript(f'vendor/{name}')

def bundledStyle(name):
    content = open(local(f'css/{name}.css'), 'r', encoding='utf-8').read()
    return f'<style type="text/css" media="screen">{content}</style>'

def bundledVendorStyle(name):
    return bundledStyle(f'vendor/{name}')


# ====================== #
# Card reviewer          #
# ====================== #

userInput = ['']
def updateUserInput(val):
    userInput[0] = val

def formatQuestion(quest):
    config = mw.addonManager.getConfig(__name__) or dict()
    hasDiff = re.search(DIFF_QUEST_PATTERN, quest, flags=re.MULTILINE)

    if (not hasDiff):
        return quest

    cleanedQuest = re.sub(DIFF_QUEST_PATTERN, '', quest, flags=re.MULTILINE)

    # Prepare editor language
    userLang = config['language']
    lang = userLang if (userLang in SUPPORTED_LANGUAGES) else 'javascript'
    langScript = bundledVendorScript(f'ace/modes/{lang}')
    
    # Prepare editor theme
    userTheme = config['theme']
    theme = userTheme if (userTheme in SUPPORTED_THEMES) else 'chrome'
    themeScript = bundledVendorScript(f'ace/themes/{theme}')

    return f'''
        {bundledStyle('CodeEditor')}

        {cleanedQuest}
        <br>
        <br>
        <div id="{EDITOR_ELEM_ID}"/>

        {bundledVendorScript('ace/ace')}
        {themeScript}
        {langScript}

        {bundledScript('CodeEditor')}
        <script>
            window.codeEditor = CodeDiffer.drawEditor('{EDITOR_ELEM_ID}' , '{userTheme}', '{userLang}');
            window.codeEditor.on('change', e => pycmd('{EVENT_CHANGED}')); 
        </script>
    '''

def formatAnswer(answer, card):
    hasDiff = re.search(DIFF_QUEST_PATTERN, answer, flags=re.MULTILINE)

    if (not hasDiff):
        return answer

    # Extract question text.
    cleanedAnswer = re.sub(DIFF_QUEST_PATTERN, '', answer, flags=re.MULTILINE)
    quest = re.sub(DIFF_ANSW_PATTERN, '', cleanedAnswer, flags=re.MULTILINE)

    # Extract user's input.
    global userInput
    userAnswer = userInput[0]

    # Extract correct answer.
    correctAnswer = re.search(DIFF_ANSW_PATTERN, answer, flags=re.MULTILINE).groups()[0]
    correctAnswer = stripHTML(correctAnswer.replace('<br>', '\n').replace('<div>', '\n'))

    return f'''
        {bundledVendorStyle('diff2html')}

        {bundledVendorScript('diff.min')}
        {bundledVendorScript('diff2html')}
        {bundledVendorScript('diff2html_ui')}
        {bundledScript('CodeDiffer')}

        {quest}
        <br>
        <br>

        <select id="diffMode">
            <option value="side-by-side">side-by-side</option>
            <option value="line-by-line">line-by-line</option>
        </select>
        <br>
        <br>

        <div id="{DIFFER_ELEM_ID}" />

        <script>
            CodeDiffer.drawDiffer('{DIFFER_ELEM_ID}', 'side-by-side', `{correctAnswer}`, `{userAnswer}`);

            document.querySelector('#diffMode').addEventListener('change', function (e) {{
                CodeDiffer.drawDiffer('{DIFFER_ELEM_ID}', e.target.value, `{correctAnswer}`, `{userAnswer}`);
            }});
        </script>
    '''

def onPrepareQA(text, card, state):
    if (state == QUESTION):
        return formatQuestion(text)
    elif (state == ANSWER):
        return formatAnswer(text, card)
    
    return text

def wrapOnCmd(onCmd):
    def _onCmd(str):
        if (str == EVENT_CHANGED):
            mw.web.evalWithCallback('window.codeEditor.getValue()', updateUserInput)
            return
        return onCmd(str)
    
    return _onCmd


def enhanceReviewer():
    mw.reviewer._linkHandler = wrapOnCmd(mw.reviewer._linkHandler)
    addHook('prepareQA', onPrepareQA)


# ====================== #
# Card editor            #
# ====================== #

def onInsertEditor(editor):
    editor.web.eval('setFormat("insertText", "[diff][/diff]");')

def onWrapInDiffer(editor):
    editor.web.eval('wrap("[diff-answ]", "[/diff-answ]");')

def enahceEditorButtons(buttons, editor):
    editor._links['insertEditor'] = onInsertEditor
    editor._links['wrapInDiffer'] = onWrapInDiffer

    return [
        editor._addButton(
            local('coding.png'),
            "insertEditor",
            "Insert code-editor tag."),
        
        editor._addButton(
            local('analytics.png'),
            "wrapInDiffer",
            "Wrap selected text in code-differ.")
    ] + buttons


# ====================== #
# Entry point            #
# ====================== #

addHook("profileLoaded", enhanceReviewer)
addHook("setupEditorButtons", enahceEditorButtons)