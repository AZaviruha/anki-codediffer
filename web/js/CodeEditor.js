;(function () {

function drawEditor(id, theme='solarized_dark', lang='javascript') {
    try {
        const editor = ace.edit(id);

        editor.setTheme('ace/theme/'+theme);
        editor.session.setMode('ace/mode/'+lang);
        editor.setFontSize(16);
        editor.focus();

        return editor;
    } catch (err) {
        console.error('CodeEditor :: ', err);
        alert(err)
    }
}

window.CodeDiffer = window.CodeDiffer || {};
window.CodeDiffer.drawEditor = drawEditor;
})();
