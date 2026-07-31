document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".btn-cart-add").forEach(button => {

        button.addEventListener("click", function (e) {

            e.preventDefault();

            const productId = this.dataset.product;

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })

            .then(r => r.json())

            .then(data => {

                document.getElementById("cartCount").innerText =
                    data.cart_count;

                showToast(data.message);

            });

        });

    });

});