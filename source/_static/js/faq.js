function openElementByAnchor() {
  // Get the anchor from the URL
  var urlFragment = document.URL.split(/#(.*)/s)[1];

  // Get the element with the anchored ID, then walk up the DOM to a details tag
  var elAnchor = document.getElementById(urlFragment);
  while (elAnchor !== null && elAnchor.tagName !== "DETAILS") {
    elAnchor = elAnchor.parentElement;
  }
  if (elAnchor === null) {
    return;
  }

  // Open the details tag
  elAnchor.open = true;
}

window.addEventListener("load", openElementByAnchor);
window.navigation.addEventListener("navigate", openElementByAnchor);
