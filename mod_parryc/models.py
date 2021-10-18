from database import db


class Entry(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.Text)
    meaning = db.Column(db.Text)

    def __repr__(self):
        return f"<{self.id} {self.word}>"
