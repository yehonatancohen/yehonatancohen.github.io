const template = 'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Language,Photo,Group Membership,Phone 1 - Type,Phone 1 - Value'

document.getElementById('generate-csv').addEventListener('click', function() {
    let prefix = document.getElementById('prefix').value;
    let amount = document.getElementById('amount').value;
    if (amount === '') {
        amount = 50;
    }
    if (prefix === '') {
        prefix = 'P';
    }
    let phoneNumbers = document.getElementById('phone-numbers').value.split(',');
    const fileInput = document.getElementById('file-input');
    let allFilesContent = []; // Array to store the content of all files

    if (fileInput.files.length > 0) {
        const files = fileInput.files;
        let filesProcessed = 0; // Keep track of the files processed

        Array.from(files).forEach(file => {
            const fileName = file.name;
            const fileExtension = fileName.slice(fileName.lastIndexOf('.')).toLowerCase();
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                // Check if the file is an Excel file
                if (fileExtension === '.xls' || fileExtension === '.xlsx') {
                    let fileContent = readExcelFile(text);
                    allFilesContent.push(fileContent);
                }
                else
                {
                    allFilesContent.push(text); // Add file content to array
                }

                processFile(allFilesContent);
            };
            if (fileExtension === '.xls' || fileExtension === '.xlsx') {
                reader.readAsBinaryString(file);
            } else {
                reader.readAsText(file);
            }
        });
    } else {
        // Or process the manual input
        processPhoneNumbers(phoneNumbers);
    }

    function processFile(allFilesContent) {
        let allLines = new Set(); // Use a set to automatically remove duplicates

        // Iterate over each file's content
        allFilesContent.forEach(content => {
            // Assume the file's content is split by newlines
            const lines = content.split(/\r?\n/);
            lines.forEach(line => {
                line = line.match(/(?:\+972|0)?(?:-)?(?:5[0-9])(?:-)?(?:\d(?:-)?){7}/g);
                if (line && !allLines.has(line[0])) { // Avoid adding empty lines
                    allLines.add(line[0]);
                }
            });
        });

        // Convert the set back into a string, joining with newlines
        const combinedContent = Array.from(allLines).join('\n');
        // For simplicity, this example will skip directly to processing phone numbers
        const phoneNumbers = combinedContent.match(/(?:\+972|0)?(?:-)?(?:5[0-9])(?:-)?(?:\d(?:-)?){7}/g);
        processPhoneNumbers(phoneNumbers);
    }

    function readExcelFile(data) {
        let combinedAllSheetsContent = '';
        const workbook = XLSX.read(data, {type: 'binary'});
        const allSheetsContent = [];   
        workbook.SheetNames.forEach(sheetName => {
            const worksheet = workbook.Sheets[sheetName];
            const rowObjectArray = XLSX.utils.sheet_to_row_object_array(worksheet);
            const rowStringArray = rowObjectArray.map(row => JSON.stringify(row));
            const combinedSheetContent = rowStringArray.join('\n');
            allSheetsContent.push(combinedSheetContent);
        });
        // Join all sheets' content, separated by two newlines
        combinedAllSheetsContent = allSheetsContent.join('\n\n');
        return combinedAllSheetsContent;
    }

    function processPhoneNumbers(numbers) {
        // Convert, generate names, and create CSV content
        const convertedNumbers = numbers.map(number => convertPhoneNumber(number.trim()));
        const names = generateNames(convertedNumbers, prefix, amount);
        const csvContent = generateCSVContent(convertedNumbers, names);
        downloadCSV(csvContent, 'contacts.csv');
    }

    function convertPhoneNumber(number) {
        // Implement phone number conversion logic here
        number = number.replace(/\W/g, '');
        let convertedNumbers = [];
        if (number.startsWith('0')) {
            convertedNumbers.push('+972' + number.substring(1));
        } else if (number.startsWith('+972')) {
            convertedNumbers.push(number);
        } else if (number.startsWith('972'))
        {
            convertedNumbers.push('+' + number);
        } else {
            convertedNumbers.push('+972' + number);
        }
        return convertedNumbers;
    }

    function generateNames(numbers, prefix, groupSize) {
        // Implement name generation logic here
        return numbers.map((_, index) => `${prefix}${Math.floor(index / groupSize)}`);
    }

    function generateCSVContent(numbers, names) {
        // Implement CSV content generation logic here
        let csvContent = template + '\n';
        numbers.forEach((number, index) => {
            row = names[index] + "," + names[index] + ",,,,,,,,,,,,,,,,,,,,,,,,,,," + "*MyContacts" + ",Mobile," + number+ "\n";
            csvContent += row;
        });
        return csvContent;
    }

    function downloadCSV(content, fileName) {
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});

document.getElementById('help-btn').addEventListener('click', function(event) {
    event.stopPropagation(); // Prevent click from propagating to the document
    const helpBox = document.getElementById('help-box');
    helpBox.classList.toggle('hidden');
});

document.addEventListener('click', function() {
    const helpBox = document.getElementById('help-box');
    if (!helpBox.classList.contains('hidden')) {
        helpBox.classList.add('hidden');
    }
});