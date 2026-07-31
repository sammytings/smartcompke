// ===============================
// SEARCH PRODUCTS
// ===============================

const searchBox = document.getElementById("productSearch");

searchBox.addEventListener("keyup", function () {

    const value = this.value.toLowerCase();

    document.querySelectorAll("#productTable tbody tr").forEach(row => {

        row.style.display =
            row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";

    });

});


// ===============================
// SELECT ALL
// ===============================

const checkAll = document.getElementById("checkAll");

const checks = document.querySelectorAll(".product-check");

checkAll.addEventListener("change", function () {

    checks.forEach(box => {

        box.checked = this.checked;

    });

    updateSummary();

});


// ===============================
// UPDATE SUMMARY
// ===============================

checks.forEach(box => {

    box.addEventListener("change", updateSummary);

});

function updateSummary() {

    const selected = document.querySelectorAll(".product-check:checked");

    document.getElementById("selectedCount").innerHTML = selected.length;

}


// ===============================
// DISCOUNT PREVIEW
// ===============================

const type = document.getElementById("id_discount_type");

const value = document.getElementById("id_discount_value");

const typePreview = document.getElementById("typePreview");

const discountPreview = document.getElementById("discountPreview");

function updateDiscount() {

    if (type) {

        if (type.value === "percent") {

            typePreview.innerHTML = "Percentage";

        }

        else if (type.value === "fixed") {

            typePreview.innerHTML = "Fixed Amount";

        }

        else {

            typePreview.innerHTML = "Fixed Price";

        }

    }

    if (value) {

        discountPreview.innerHTML = value.value;

    }

}

if (type) {

    type.addEventListener("change", updateDiscount);

}

if (value) {

    value.addEventListener("keyup", updateDiscount);

    value.addEventListener("change", updateDiscount);

}

updateSummary();

updateDiscount();


// ===============================
// HIGHLIGHT ROW
// ===============================

checks.forEach(box => {

    box.addEventListener("change", function () {

        if (this.checked) {

            this.closest("tr").classList.add("selected-row");

        }

        else {

            this.closest("tr").classList.remove("selected-row");

        }

    });

});