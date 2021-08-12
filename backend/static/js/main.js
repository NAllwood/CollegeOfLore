function toggleTheme() {
    const htmlTag = document.getElementsByTagName('html')[0]
    if (htmlTag.hasAttribute('data-theme')) {
        let theme = htmlTag.getAttribute('data-theme')

        switch (theme) {
            case "light":
                htmlTag.setAttribute('data-theme', 'default')
                window.localStorage.removeItem("site-theme", "default")
                break;
            default:
                htmlTag.setAttribute('data-theme', 'light')
                window.localStorage.setItem("site-theme", "light")
                break;
        }
    }
}

function applyInitialTheme() {
    const theme = window.localStorage.getItem("site-theme")
    if (theme !== null) {
        const htmlTag = document.getElementsByTagName("html")[0]
        htmlTag.setAttribute("data-theme", theme)
    }
}

applyInitialTheme();

document
    .getElementById("theme-toggle")
    .addEventListener("click", toggleTheme);
