class MusicTreeException(Exception):
    pass


class AddChordError(MusicTreeException):
    def __init__(self):
        msg = f"Use Part.add_chord() instead!"
        super().__init__(msg)


class AlreadyFinalizedError(MusicTreeException):
    def __init__(self, object_, method_=None):
        msg = f"{object_.__class__.__name__} is already finalized."
        if method_:
            msg += f' Method {object_.__class__.__name__}.{method_}() cannot be called after finalization.'
        super().__init__(msg)


class DeepCopyException(MusicTreeException):
    pass


class WrongNumberOfChordsError(MusicTreeException):
    pass


# Beat exceptions


class BeatException(MusicTreeException):
    pass


class BeatWrongDurationError(BeatException, ValueError):
    pass


class BeatIsFullError(BeatException):
    pass


class BeatNotFullError(BeatException):
    pass


class BeatHasNoParentError(BeatException):
    pass


class BeatHasWrongTupletError(BeatException):
    pass


# Chord exceptions
class ChordException(MusicTreeException):
    pass


class ChordAddXException(ChordException):
    pass


class ChordAddXPlacementException(ChordAddXException):
    pass


class ChordAlreadySplitError(ChordException):
    pass


class ChordCannotSplitError(ChordException):
    pass


class ChordHasNoMidisError(ChordException):
    pass


class ChordHasNoParentError(ChordException):
    pass


class ChordHasNoQuarterDurationError(ChordException):
    pass


class ChordNotesAreAlreadyCreatedError(ChordException):
    pass


class ChordQuarterDurationAlreadySetError(ChordException):
    pass


# Lyrics exceptions

class LyricsException(MusicTreeException):
    pass


class LyricsExtensionError(LyricsException):
    pass


class LyricSyllabicOrExtensionError(LyricsException):
    pass


class LyricsWrongNumberOfChordsError(LyricsException):
    pass


# Measure exceptions
class MeasureException(MusicTreeException):
    pass


# Metronome exceptions
class MetronomeException(MusicTreeException):
    pass


class MetronomeWrongBeatUnitError(MetronomeException):
    pass


# Note exceptions
class NoteException(MusicTreeException):
    pass


class NotationException(NoteException):
    pass


class NoteHasNoParentChordError(NoteException):
    pass


class NoteMidiHasNoParentChordError(NoteException):
    pass


class NoteTypeError(NoteException):
    pass


# Part exceptions
class PartException(MusicTreeException):
    pass


# Staff exceptions

class StaffException(MusicTreeException):
    pass


class StaffHasNoParentError(StaffException):
    pass


# Voice exceptions
class VoiceException(MusicTreeException):
    pass


class VoiceHasNoBeatsError(VoiceException):
    pass


class VoiceHasNoParentError(VoiceException):
    pass


class VoiceIsFullError(VoiceException):
    pass


# Id exceptions (see Part)

class IdException(MusicTreeException):
    pass


class IdHasAlreadyParentOfSameTypeError(IdException):
    pass


class IdWithSameValueExistsError(IdException):
    pass


# QuarterDuration exceptions
class QuarterDurationException(MusicTreeException):
    pass


class QuarterDurationIsNotWritable(QuarterDurationException):
    pass


# Score exceptions
class ScoreException(MusicTreeException):
    pass


# SimpleFormat exceptions
class SimpleFormatException(MusicTreeException):
    pass