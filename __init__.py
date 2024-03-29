import re
from os import listdir
from os.path import dirname, abspath, isfile, join, splitext

from aqt import mw
from anki.hooks import addHook, runHook
from anki.utils import stripHTML
from aqt.utils import showInfo
from aqt.qt import *
from aqt.reviewer import Reviewer


# ====================== #
# Consts                 #
# ====================== #

QUESTION = 'reviewQuestion'
ANSWER = 'reviewAnswer'
DIFF_QUEST_PATTERN = r'\[diff(.*)?\].*\[/diff\]'
DIFF_ANSW_PATTERN = r'\[diff-answ\](.*)\[/diff-answ\]'
LANG_ATTR_PATTERN = r'lang=[\'"](.*?)[\'"]'
THEME_ATTR_PATTERN = r'theme=[\'"](.*?)[\'"]'

EVENT_CHANGED = 'CUSTOM::answerChanged'
EDITOR_ELEM_ID = 'codeEditor'
DIFFER_ELEM_ID = 'codeDiffer'

modesDir = join(dirname(abspath(__file__)), 'web/js/vendor/ace/modes')
modeFiles = [f for f in listdir(modesDir) if isfile(join(modesDir, f))]
SUPPORTED_LANGUAGES = [splitext(f)[0] for f in modeFiles if f.endswith('js')]

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
    current = dirname(abspath(__file__))
    return f'{current}/{path}'

def bundledScript(name):
    content = open(local(f'web/js/{name}.js'), 'r', encoding='utf-8').read()
    return f'<script type="text/javascript">{content}</script>'

def bundledVendorScript(name):
    return bundledScript(f'vendor/{name}')

def bundledStyle(name):
    content = open(local(f'web/css/{name}.css'), 'r', encoding='utf-8').read()
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

    attrs = hasDiff.groups()[0] or ''

    # Prepare editor language
    cardLang = re.search(LANG_ATTR_PATTERN, attrs)
    cardLang = cardLang.groups()[0] if cardLang else None
    confLang = config['language']
    userLang = cardLang or confLang
    lang = userLang if (userLang in SUPPORTED_LANGUAGES) else 'javascript'
    langScript = bundledVendorScript(f'ace/modes/{lang}')
    
    # Prepare editor theme
    cardTheme = re.search(THEME_ATTR_PATTERN, attrs)
    cardTheme = cardTheme.groups()[0] if cardTheme else None
    confTheme = config['theme']
    userTheme = cardTheme or confTheme
    theme = userTheme if (userTheme in SUPPORTED_THEMES) else 'chrome'
    themeScript = bundledVendorScript(f'ace/themes/{theme}')

    # Prepare question text
    cleanedQuest = re.sub(DIFF_QUEST_PATTERN, '', quest, flags=re.MULTILINE)

    return f'''
        {bundledStyle('CodeEditor')}

        {cleanedQuest}
        <br>
        <br>
        <div id="{EDITOR_ELEM_ID}"></div>

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

        <div id="{DIFFER_ELEM_ID}"></div>

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
    editor.web.eval('setFormat("insertText", "[diff lang=\'javascript\'][/diff]");')

def onWrapInDiffer(editor):
    editor.web.eval('wrap("[diff-answ]", "[/diff-answ]");')


def enahceEditorButtons(buttons, editor):
    editor._links['insertEditor'] = onInsertEditor
    editor._links['wrapInDiffer'] = onWrapInDiffer

    return [
        editor._addButton(
            local('resources/coding.png'),
            "insertEditor",
            "Insert code-editor tag."),
        
        editor._addButton(
            local('resources/diff.png'),
            "wrapInDiffer",
            "Wrap selected text into code-differ.")
    ] + buttons


# ====================== #
# Entry point            #
# ====================== #

addHook("profileLoaded", enhanceReviewer)
addHook("setupEditorButtons", enahceEditorButtons)