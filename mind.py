import log

class Mind:
    def __init__(self):
        self.empty  = True
        self._state = dict()


    def update(self, message):
        for word in self._state:
            self._state[word]["ttl"] -= 1

        for word in message.components:
            self._state[word] = {
                "message": log.Message(word, message.offset),
                "ttl":     10,
            }

        new_state = dict()
        for word in self._state:
            if self._state[word]["ttl"] >= 0:
                new_state[word] = self._state[word]
        self._state = new_state
        self.empty  = False


    def messages(self):
        return [ self._state[word]["message"] for word in self._state ]


    def __str__(self):
        content = "TTL\tWord\n"
        ordered = sorted(self._state.values(), key=lambda item: item['ttl'], reverse=True)
        for word in ordered:
            content += "{: 3}\t{}\n".format(word["ttl"], word["message"])
        return content

