import ratings


class Parser:

    def __init__(self, url):
        # Global variables
        self.address = url
        self.list = 'leanings.txt'
        self.trusted = ['bbc',
                        'npr',
                        'pbs',
                        'wsj',
                        'abc',
                        'cbs',
                        'nbc',
                        'cnn',
                        'usatoday']

    def parse(self):
        # Sends address to recommended and not recommended methods.
        # Returns a recommendation
        r = self.recommended()
        nr = self.not_recommended()
        r_score = r - nr + self.compare_known_sources()
        if r_score > 1:
            return ratings.Ratings.RECOMMENDED
        elif r_score < -1:
            return ratings.Ratings.NOT_RECOMMENDED
        else:
            return ratings.Ratings.UNCERTAIN

    def not_recommended(self):
        # Assigns a not_recommended score to a url
        score = 0
        # Check for known urls
        if 'com.co' in self.address:
            score -= 2
        return score

    def recommended(self):
        # Assigns a recommended score to a url
        score = 0
        # Check for known urls
        for s in self.trusted:
            if s in self.address:
                score += 1
        return score

    def build_leanings_index(self):
        # Returns leanings of known sources
        leanings = []
        filename = self.list
        with open(filename) as inputfile:
            for line in inputfile:
                leanings.append(line.strip().split('\t'))
        return leanings

    def compare_known_sources(self):
        # Returns a -1, 0, or 1 depending on source leanings
        index = self.build_leanings_index()
        for i in index:
            print
            i
            if self.address in i[3]:
                if i[1] is 'Center':
                    return 1
                else:
                    return -1
        return 0