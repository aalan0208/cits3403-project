// Wait for the DOM to be fully loaded
$(document).ready(function () {
    // Event listener for the "Save Question" button click
    $("#saveQuestion").click(function () {
        // Extract the title from the input field
        var questionTitle = $("#questionText").val();

        // Create a new box element
        var newBox = $("<div class='box'></div>");

        // Create a new quiz title element
        var quizTitle = $("<div class='quiz-title text center'></div>").text(questionTitle);

        // Append the quiz title to the new box
        newBox.append(quizTitle);

        // Append the new box to the container
        $("#questionList").append(newBox);
    });

    // Event listener for the form submission
    $('form').submit(function () {
        // Update the hidden input field with the latest questions data
        $('#questionsData').val(JSON.stringify(questions));
    });

    // Event listener for the "Create Question Modal" shown
    $('#createQuestionModal').on('shown.bs.modal', function () {
        $('#questionText').trigger('focus');
    });

    // Initialize the questions array
    let questions = [];

    // Event listener for the "Save Question" button click
    $('#saveQuestion').click(function () {
        // Extract values from the input fields
        let questionText = $('#questionText').val();
        let answerOne = $('#answerOne').val();
        let answerTwo = $('#answerTwo').val();
        let answerThree = $('#answerThree').val();
        let answerFour = $('#answerFour').val();
        let correctAnswer = $('#correctAnswer').val();

        // Create a question object
        let question = {
            questionText: questionText,
            answerOne: answerOne,
            answerTwo: answerTwo,
            answerThree: answerThree,
            answerFour: answerFour,
            correctAnswer: correctAnswer
        };

        // Add question to the questions array
        questions.push(question);

        // Update the hidden input field with the questions array
        $('#questionsData').val(JSON.stringify(questions));

        // Optionally, clear the form fields
        $('#questionForm')[0].reset();

        // Close the modal
        $('#createQuestionModal').modal('hide');
    });
});
