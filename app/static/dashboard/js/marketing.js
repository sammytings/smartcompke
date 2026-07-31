// ==========================================
// PRODUCT SEARCH
// ==========================================

const searchInput = document.getElementById("searchProduct");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        document.querySelectorAll("#productsTable tbody tr").forEach(row => {

            row.style.display = row.innerText.toLowerCase().includes(value)
                ? ""
                : "none";

        });

    });

}


// ==========================================
// SELECT ALL PRODUCTS
// ==========================================

const checkAll = document.getElementById("checkAll");

const checkboxes = document.querySelectorAll(".product-check");

if (checkAll) {

    checkAll.addEventListener("change", function () {

        checkboxes.forEach(box => {

            box.checked = this.checked;

            highlightRow(box);

        });

        updateSummary();

    });

}


// ==========================================
// ROW HIGHLIGHT
// ==========================================

function highlightRow(box){

    const row = box.closest("tr");

    if(box.checked){

        row.classList.add("selected-row");

    }

    else{

        row.classList.remove("selected-row");

    }

}


// ==========================================
// LIVE SUMMARY
// ==========================================

function updateSummary(){

    const total = document.querySelectorAll(".product-check:checked").length;

    document.getElementById("selectedProducts").innerHTML = total;

}


// ==========================================
// SUBJECT PREVIEW
// ==========================================

const subject = document.getElementById("id_subject");

const subjectPreview = document.getElementById("subjectPreview");

if(subject){

    subject.addEventListener("keyup", function(){

        subjectPreview.innerHTML =

            this.value || "--";

    });

}


// ==========================================
// EVENTS
// ==========================================

checkboxes.forEach(box => {

    box.addEventListener("change", function(){

        highlightRow(this);

        updateSummary();

    });

});


// ==========================================
// EMAIL PREVIEW
// ==========================================

const previewButton = document.querySelector(".btn-preview");

if(previewButton){

    previewButton.addEventListener("click", function(){

        const subject = document.getElementById("id_subject").value;

        const message = document.getElementById("id_message").value;

        const selected = document.querySelectorAll(".product-check:checked").length;

        alert(

`EMAIL PREVIEW

Subject:
${subject}

Selected Products:
${selected}

Message:

${message}

A professionally designed marketing email will be sent to all registered users.`

        );

    });

}


// ==========================================
// INITIALIZE
// ==========================================

updateSummary();