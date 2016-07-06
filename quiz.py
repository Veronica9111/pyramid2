
class Quiz_Handler:

    def __init__(self, file):
        self._file = file;

    def get_items(self):
        lines = []
        quiz = []
        lines = self._file.readlines()
        for line in lines:
            line = line.split(',')
            (question, answer) = line[:2]
            if question == "" and answer == "":
                continue
            else:
                quiz.append({'question': question, 'answer': answer})
        return quiz

if  __name__ == '__main__':
    qh = Quiz_Handler('/Users/veronica/Desktop/quiz.csv')
    qh.handle()

