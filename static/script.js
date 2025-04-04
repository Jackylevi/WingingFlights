console.log("script.js loaded"); // Check if the script file runs at all

const flightForm = document.getElementById('flight-form');

if (flightForm) {
    console.log("Form element #flight-form found."); // Check if the element is found

    flightForm.addEventListener('submit', function(event) {
        console.log("Submit event listener fired!"); // Check if the listener is triggered

        event.preventDefault(); // Prevent default form submission
        console.log("event.preventDefault() called."); // Check if this line is reached

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const messageDiv = document.getElementById('response-message');
        console.log("Form data captured:", data); // See the data collected

        // Basic validation example (more can be added)
        if (parseInt(data.min_days) > parseInt(data.max_days)) {
            messageDiv.textContent = 'Error: Minimum days cannot be greater than maximum days.';
            messageDiv.className = 'error';
            console.log("Validation failed: min_days > max_days");
            return;
        }

        messageDiv.textContent = 'Subscribing...';
        messageDiv.className = ''; // Clear previous styles

        console.log("Attempting fetch to /subscribe..."); // Check before fetch

        fetch('/subscribe', { // Send data to the backend endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => {
            console.log("Fetch response received:", response.status); // Log response status
            if (!response.ok) {
                // Try to get error message from backend, or use default
                return response.json().then(err => { throw new Error(err.error || 'Subscription failed. Please try again.') });
            }
            return response.json();
        })
        .then(result => {
            console.log("Fetch success:", result); // Log success result
            messageDiv.textContent = result.message || 'Subscription successful! Check your email for deals.';
            messageDiv.className = 'success';
            form.reset(); // Clear the form
        })
        .catch(error => {
            console.error('Fetch Error:', error); // Log any fetch errors
            messageDiv.textContent = `Error: ${error.message}`;
            messageDiv.className = 'error';
        });

        console.log("Submit event listener finished."); // Check if the listener function completes

    }); // End of addEventListener

} else {
    console.error("Form element #flight-form NOT found!"); // Error if form isn't found
}