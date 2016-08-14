angular.module("chatboxApp").controller(
    "chatboxCtrl",
    function($http, $scope) {
        var ctrl = this;
        $scope.messages = [];

        /**
         * Send a message to the backend.
         * @param msg The message object to be sent. This should contain
         *            'author' and 'message' keys.
         */
        ctrl.sendMessage = function(msg) {
            $http.post(
                "/messages",
                JSON.stringify(msg)
            )
        };

        /**
         * The function to be called whenever the "send" button is clicked.
         * This should delegate actually sending the message to `sendMessage`.
         */
        ctrl.onSendClicked = function() {
            ctrl.sendMessage({
                author: $scope.author,
                message: $scope.message
            })
        };

        /**
         * The function to be fired whenever we receive a message event from
         * the server. This should parse the JSON data and add it to our list
         * of messages in the scope.
         * @param event An event object from the server.
         */
        ctrl.onMessageEvent = function(event) {
            var msg = JSON.parse(event.data);
            $scope.messages.push(msg);
            $scope.$digest();  // Force Angular to refresh its models.
        };

        /**
         * Retrieve messages from the backend and load them into our scope.
         * @param n The maximum number of messages that should be retrieved.
         */
        ctrl.loadMessages = function(n) {
            $http.get("/messages", {
                params: {"max": n}
            }).then(function(response) {
                $scope.messages = response.data.slice().reverse();
            });
        };

        // Register an event source listener callback.
        var es = new EventSource("/messages/subscribe");
        es.addEventListener("message", ctrl.onMessageEvent);

        // Load the latest 10 messages onto the UI.
        ctrl.loadMessages(10);
    }
);


