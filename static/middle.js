function extract_title() {
    // get element by ID of the quiz
    var extract_title = document.getElementById("quizTitle")
    // extract the value of the title and store it in title
    var title = extract_title.value
    // returns the title
    return title;
}

function submit_form() {
    quiz_title = extract_title()
    console.log("form submitted")
}


var questions = []; // Array to store questions
function openCreateQuestionPopup() {
    // Calculate the position for centering the pop-up window
    var width = 600;
    var height = 400;
    var left = (window.innerWidth / 2) - (width / 2);
    var top = (window.innerHeight / 2) - (height / 2);
    // Open a new window for creating a question
    var createQuestionPopup = window.open("/createQuestion", "CreateQuestionPopup", "width=" + width + ",height=" + height + ",left=" + left + ",top=" + top);
    // Listen for message from the popup window
    window.addEventListener("message", function (event) {
        // Add the question to the array only if it doesn't already exist
        var question = event.data;
        if (!questions.some(q => q.question === question.question)) {
            questions.push(question);
            updateQuestionList();
        }
    });
}
function updateQuestionList() {
    var questionList = document.getElementById("questionList");
    questionList.innerHTML = ''; // Clear existing questions
    // Loop through questions and add them to the list
    questions.forEach(function (question, index) {
        var listItem = document.createElement("li");
        // Create a div to hold the question
        var questionDiv = document.createElement("div");
        questionDiv.textContent = "Question: " + question.question;
        listItem.appendChild(questionDiv);
        // Create a ul element to hold the answers
        var answerList = document.createElement("ul");
        // Add correct answer
        var correctAnswerItem = document.createElement("li");
        correctAnswerItem.textContent = "Correct Answer: " + question.correctAnswer;
        answerList.appendChild(correctAnswerItem);
        // Add wrong answers
        question.wrongAnswers.forEach(function (wrongAnswer) {
            var wrongAnswerItem = document.createElement("li");
            wrongAnswerItem.textContent = "Wrong Answer: " + wrongAnswer;
            answerList.appendChild(wrongAnswerItem);
        });
        // Append answer list to the list item
        listItem.appendChild(answerList);
        // Create a delete button
        var deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className = "btn btn-danger btn-sm";
        deleteButton.style.marginTop = "10px";
        deleteButton.onclick = function () {
            deleteQuestion(index);
        };
        listItem.appendChild(deleteButton);
        // Append list item to the question list
        questionList.appendChild(listItem);
    });
}

function deleteQuestion(index) {
    questions.splice(index, 1); // Remove the question from the array
    updateQuestionList(); // Update the question list
}


function saveQuiz() {
    var quizTitle = document.getElementById("quizTitle").value;

    // Create a new div element for the quiz box
    var quizBox = document.createElement("div");
    quizBox.classList.add("box");

    // Create a div for the title and add it to the quiz box
    var titleDiv = document.createElement("div");
    titleDiv.classList.add("quizTitle");
    titleDiv.textContent = quizTitle;
    quizBox.appendChild(titleDiv);

    // Append the quiz box to the quiz container
    var quizContainer = document.getElementById("quizContainer");
    quizContainer.appendChild(quizBox);

}
function saveQuizAndRedirect(event) {
    event.preventDefault();  // Prevent the default anchor action
    saveQuiz();              // Call the saveQuiz function
    window.location.href = "/main.html";  // Redirect to another page (corrected URL)
}