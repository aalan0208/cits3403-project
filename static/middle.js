function extract_title(){
    // get element by ID of the quiz
    var extract_title = document.getElementById("quizTitle")
    // extract the value of the title and store it in title
    var title = extract_title.value
    // returns the title
    return title;
}

