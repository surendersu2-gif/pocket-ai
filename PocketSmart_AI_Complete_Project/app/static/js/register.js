const registerForm = document.querySelector("#registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const errorBox = document.querySelector("#error");

        if (errorBox) {
            errorBox.textContent = "";
        }

        try {
            const nameInput = document.querySelector("#name");
            const emailInput = document.querySelector("#email");
            const passwordInput = document.querySelector("#password");

            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value;

            const response = await fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                let message = "Registration failed.";

                if (typeof data.detail === "string") {
                    message = data.detail;
                } else if (Array.isArray(data.detail)) {
                    message = data.detail
                        .map(x => x.msg || JSON.stringify(x))
                        .join(", ");
                } else if (data.detail) {
                    message = JSON.stringify(data.detail);
                }

                throw new Error(message);
            }

            if (data.access_token) {
                localStorage.setItem(
                    "pocketsmart_token",
                    data.access_token
                );
            }

            if (data.user) {
                localStorage.setItem(
                    "pocketsmart_user",
                    JSON.stringify(data.user)
                );
            }

            window.location.href = "/dashboard";

        } catch (error) {
            if (errorBox) {
                errorBox.textContent =
                    error.message || "Registration failed.";
            }

            console.error("Registration error:", error);
        }
    });
}
