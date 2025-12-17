// Get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Get CSRF token from hidden input or cookie
function getCSRFToken() {
  let csrftoken = $("[name=csrfmiddlewaretoken]").val();
  if (!csrftoken) {
    csrftoken = getCookie("csrftoken");
  }
  return csrftoken;
}

// Make AJAX request with CSRF token
function makeAjaxRequest(url, method, successCallback, errorCallback) {
  $.ajax({
    url: url,
    method: method,
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "X-Requested-With": "XMLHttpRequest",
    },
    success: successCallback,
    error: errorCallback,
  });
}

//messaging system
function displayMessage(message, status) {
  if (!message) return; // Don't display if no message
  
  let alertContainer = $("<div class='alert p-3 rounded mb-2'></div>");
  alertContainer.insertBefore("main");
  
  if (status == 200 || status == 'success') {
    alertContainer.addClass("bg-green-100 text-green-700 border border-green-300");
  } else {
    alertContainer.addClass("bg-red-100 text-red-700 border border-red-300");
  }
  
  alertContainer.html(message);
  
  setTimeout(function () {
    alertContainer.fadeOut("slow", function () {
      $(this).remove();
    });
  }, 3000);
}
