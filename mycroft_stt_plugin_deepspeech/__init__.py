import deepspeech
import numpy
import time
from mycroft.stt import STT
from mycroft.util.log import LOG


class DeepspeechSTTPlugin(STT):
    def __init__(self):
        super().__init__()

        start_time = time.perf_counter()
        LOG.info("Loading DeepSpeech model...")

        model = self.config['model']
        alphabet = self.config['alphabet']
        num_context = self.config.get('num_context', 9)
        beam_width = self.config.get('beam_width', 512)
        num_features = self.config.get('num_features', 26)
        lm = self.config.get('lm')
        trie = self.config.get('trie')

        self.model = deepspeech.Model(model, num_features, num_context,
                                      alphabet, beam_width)

        if lm is not None and trie is not None:
            lm_weight = self.config.get('lm_weight', 1.5)
            vwcw = self.config.get('valid_word_count_weight', 2.25)

            self.model.enableDecoderWithLM(alphabet, lm, trie, lm_weight, vwcw)

        LOG.info("Loaded DeepSpeech model in %0.3fs" % (time.perf_counter() -
                                                        start_time))
        self.stream_ctx = None
        self.can_stream = True

    def execute(self, audio, language=None):
        text = self.model.finishStream(self.stream_ctx)
        self.stream_ctx = None
        LOG.info(text)
        return text

    def stream_start(self, language=None):
        self.stream_ctx = self.model.setupStream()

    def stream_data(self, data):
        self.model.feedAudioContent(
            self.stream_ctx, numpy.frombuffer(data, numpy.int16))

    def stream_stop(self):
        LOG.info("stop")
        self.stream_ctx = None
