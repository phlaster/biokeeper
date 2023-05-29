import hashlib
import random
import qrcode
import os
from sys import stderr

class Research:
    def __init__(self, id, date_start, date_end, research_type, n_samples, offset):
        self.id = id
        self.date_start = date_start
        self.date_end = date_end
        self.n_samples = n_samples
        self.research_type = research_type
        self.offset = offset
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
            self._qrs[i+1+self.offset] = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))
    
    
    def write_codes(self):
        if not self._qrs:
            print("No qr codes were generated for this research!", file=stderr)
        else:
            with open(f"research{self.id}/research{self.id}_{self.n_samples}qrs.csv", "w") as f:
                for i in range(self.n_samples):
                    print(f"{i+1+self.offset},{self._qrs[i+1+self.offset]}", file=f)
            print(f"{self.n_samples} codes have been written!", file=stderr)


    def write_pictures(self):
        if not self._qrs:
            print("No qr codes were generated for this research!", file=stderr)
        else:
            if not os.path.isdir(f"research{self.id}/"):
                os.makedirs(f"research{self.id}/")
            for i in range(self.n_samples):
                n = i+1+self.offset
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=25,
                    border=2,
                )
                qr.add_data(self._qrs[n])
                qr.make(fit=True)
                qr.make_image(fill_color="black", back_color="white").save(f"research{self.id}/{n}.svg")
            print(f"{self.n_samples} QR images have been written!", file=stderr)

r = Research(1,2,3,4,5,6)
r.write_pictures()