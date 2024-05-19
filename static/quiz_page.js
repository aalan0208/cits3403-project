$(document).ready(function () {
    let questions = [];

    // Focus on the question text when the modal is shown
    $('#createQuestionModal').on('shown.bs.modal', function () {
        $('#questionText').trigger('focus');
    });

    $('#saveQuestion').click(function () {
        // Gather the form data
        let questionText = $('#questionText').val();
        let answerOne = $('#answerOne').val();
        let answerTwo = $('#answerTwo').val();
        let answerThree = $('#answerThree').val();
        let answerFour = $('#answerFour').val();
        let correctAnswer = $('#correctAnswer').val();

        // Create a question object
        let question = {
            questionText: questionText,
            answers: [answerOne, answerTwo, answerThree, answerFour],
            correctAnswer: correctAnswer
        };

        // Append the question to the list
        questions.push(question);

        // Update the hidden input with the questions data
        $('#questionsData').val(JSON.stringify(questions));

        // Append to question list in the UI
        $('#questionList').append(
            '<li>' + questionText + '<ul>' +
            '<li>' + answerOne + '</li>' +
            '<li>' + answerTwo + '</li>' +
            '<li>' + answerThree + '</li>' +
            '<li>' + answerFour + '</li>' +
            '<li><strong>Correct Answer: </strong>' + correctAnswer + '</li>' +
            '</ul></li>'
        );

        // Clear the form
        $('#questionForm')[0].reset();

        // Close the modal
        $('#createQuestionModal').modal('hide');
    });
});
