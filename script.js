// Get necessary elements
const chatboxContainer = document.querySelector('.chatbox-container');
const textContainer = document.querySelector('.text-container');
const inputField = document.querySelector('.input-field');
const sendIcon = document.querySelector('.send-icon');

// Function to send message
function sendMessage() {
  // Get input value
  const inputValue = inputField.value;
  // Clear input field
  inputField.value = '';
  // Create new message element
  const messageElement = document.createElement('div');
  const messageText = document.createElement('p');
  // Set message text
  messageText.innerText = inputValue;
  // Add message text to message element
  messageElement.appendChild(messageText);
  // Add class to message element
  messageElement.classList.add('message-container');
  // Add message element to text container
  textContainer.appendChild(messageElement);
  // Scroll to bottom of text container
  textContainer.scrollTop = textContainer.scrollHeight;
}

// Add event listener for send button
sendIcon.addEventListener('click', sendMessage);

// Add event listener for enter key press
inputField.addEventListener('keydown', (event) => {
  if (event.keyCode === 13) {
    sendMessage();
  }
});

function sendMessage(event) {
    event.preventDefault();

    // get the user message
    var userMessage = document.getElementById('user-message').value;

    // create a new message container and add the user message
    var messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container', 'user');
    var messageText = document.createElement('p');
    messageText.innerText = userMessage;
    messageContainer.appendChild(messageText);
    document.querySelector('.messages-container').appendChild(messageContainer);

    // send the user message to the server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/message');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status === 200) {
            // create a new message container and add the reply message
            var replyContainer = document.createElement('div');
            replyContainer.classList.add('message-container', 'bot');
            var replyText = document.createElement('p');
            replyText.innerText = xhr.responseText;
            replyContainer.appendChild(replyText);
            document.querySelector('.messages-container').appendChild(replyContainer);
        }
        else {
            alert('Request failed. Returned status of ' + xhr.status);
        }
    };
    xhr.send('message=' + encodeURIComponent(userMessage));

    // clear the input field
    document.getElementById('user-message').value = '';

    // scroll to the bottom of the messages container
    var messagesContainer = document.querySelector('.messages-container');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

