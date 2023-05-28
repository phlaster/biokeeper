import hashlib
import random
from sys import stderr

class Research:
    def __init__(self, id, date_start, date_end, research_type, n_samples):
        self.id = id
        self.date_start = date_start
        self.date_end = date_end
        self.n_samples = n_samples
        self.research_type = research_type
        self._qrs = {}

        self.generate_qrs()


    def get_qrs(self):
        return self._qrs


    def public_fields_digest(self):
        fields = [str(v) for k, v in self.__dict__.items() if not k.startswith("_")]
        return "".join(fields)


    def generate_qrs(self, length = 16):
        random.seed(self.public_fields_digest())
        for i in range(self.n_samples):
            self._qrs[i+1] = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))
    
    
    def write_codes(self):
        if not self._qrs:
            print("No qr codes were generated for this research!", file=stderr)
        else:
            with open(f"research{self.id}_{self.n_samples}qrs.csv", "w") as f:
                for i in range(self.n_samples):
                    print(f"{i+1},{self._qrs[i+1]}", file=f)
            print(f"{self.n_samples} codes have been written!", file=stderr)

