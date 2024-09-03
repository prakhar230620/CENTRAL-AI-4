$(document).ready(function() {
    let isListening = false;
    let recognition;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function(event) {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    $('#user-input').val(event.results[i][0].transcript);
                    stopListening();
                    sendInput('voice');
                } else {
                    interimTranscript += event.results[i][0].transcript;
                    $('#user-input').val(interimTranscript);
                }
            }
        };
    }

    $('#send-btn').click(function() {
        sendInput('text');
    });

    $('#mic-btn').click(function() {
        if (!isListening) {
            startListening();
        } else {
            stopListening();
        }
    });

    function sendInput(type) {
        let input = $('#user-input').val();
        $.ajax({
            url: '/process_input',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ input: input, type: type }),
            success: function(response) {
                displayResponse(response.response);
                if (response.audio_file) {
                    playAudioResponse(response.audio_file);
                }
            },
            error: function(xhr, status, error) {
                displayResponse("Error: " + error);
            }
        });
    }

    function displayResponse(response) {
        $('#response-area').append(`<p class="ai-response">${response}</p>`);
        $('#response-area').scrollTop($('#response-area')[0].scrollHeight);
    }

    function startListening() {
        if (recognition) {
            isListening = true;
            $('#mic-btn').removeClass('btn-secondary').addClass('btn-danger');
            recognition.start();
        } else {
            alert("Speech recognition is not supported in your browser.");
        }
    }

    function stopListening() {
        if (recognition) {
            isListening = false;
            $('#mic-btn').removeClass('btn-danger').addClass('btn-secondary');
            recognition.stop();
        }
    }

    function playAudioResponse(audioFile) {
        let audio = new Audio(audioFile);
        audio.play();
    }
});