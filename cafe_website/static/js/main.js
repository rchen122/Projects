function selectItem(itemId) {
    fetch(`/select_item`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: itemId }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Replace the selected item's table cell with quantity selection
            // const selectedCell = document.querySelector(`[data-item-id="${itemId}"]`);

            const selectedCell = document.getElementById(`item-${itemId}`)
            selectedCell.innerHTML = `
                <label for="quantity">Quantity:</label>
                <input type="number" id="quantity-${itemId}" min="1" value="1">
                <button onclick="cancelSelection(${itemId}, '${data.item_name}')">Cancel</button>
                <button onclick="confirmSelection(${itemId})">Confirm</button>
            `;
        })
        .catch((error) => console.error("Error:", error));
}

function confirmSelection(itemId) {
    const quantityInput = document.getElementById(`quantity-${itemId}`);
    const quantity = quantityInput.value;
    
    fetch(`/add_item`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({id: itemId, quantity: quantity})
    })
        .then((response) => response.json())
        .then((data) => {
            const cartDiv = document.getElementById('cart');
            cartDiv.innerHTML = data.cart_html;

            const itemCell = document.getElementById(`item-${itemId}`)
            itemCell.innerHTML = `
                <a href="#" onclick="selectItem(${itemId})"> ${data.item_name}</a>
            `
        })
        .catch((error) => {
            console.error("Error: ", error)
        })

}

function cancelSelection(itemId, item_name) {
    const selectedCell = document.getElementById(`item-${itemId}`);
    selectedCell.innerHTML = `
        <a href="#" onclick="selectItem(${itemId})"> ${item_name}</a>
    `;
}

function check_credentials(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch(`/submit_login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"username": username, "password": password})
    })
    .then((response => response.json()))
    .then(data => {
        // Clear any existing error message
        const errorDiv = document.getElementById("error-message");
        if (errorDiv) {
            errorDiv.remove();
        }
        // Check if login failed
        if (!data.success) {
            // Create an error message element
            const errorMessage = document.createElement("p");
            errorMessage.id = "error-message";
            errorMessage.style.color = "red";
            errorMessage.textContent = "Invalid Login Credentials";
            
            // Insert the error message after the form
            const form = document.querySelector("form");
            form.parentNode.insertBefore(errorMessage, form.nextSibling);
        } else {
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

    
