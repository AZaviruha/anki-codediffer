;(function () {

function drawDiffer(elemId, mode, answ1, answ2) {
    const diffString = JsDiff.createPatch('', answ1, answ2, 'Correct answer', 'Your answer');
    const diff2htmlUi = new Diff2HtmlUI({ diff: diffString });

    diff2htmlUi.draw('#'+elemId, {
        inputFormat: 'json',
        showFiles: true,
        matching: 'lines',
        outputFormat: mode,
        synchronisedScroll: true,
    });
}

window.CodeDiffer = window.CodeDiffer || {};
window.CodeDiffer.drawDiffer = drawDiffer;
})();