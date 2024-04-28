
window.onload = function() {

    setInterval(()=>{
        var elementsWithTitleAudit = $('a[title="Audit"]');
        elementsWithTitleAudit.each(function() {
        var currentText = $(this).text();
        var updatedText = currentText.replace(/\s*ر\.ع\.\s*$/, ''); // This regex removes the specific text at the end
        $(this).text(updatedText);
        });


        $('span.o_account_report_column_value').each(function() {
                debugger;

            var currentText = $(this).text();

            var updatedText = currentText.replace(/\s*ر\.ع\.\s*$/, ''); // Updated regex to match and remove the specific text

            $(this).text(updatedText.trim()); // Trim any extra whitespace


        });
    },1000)

};