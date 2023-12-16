import hashlib
import random
import string
import qrcode
import os
from sys import stderr

class Research:
    def __init__(self, research_id, day_start, day_end, research_type, n_samples, offset):
        self.research_id = research_id
        self.day_start = day_start
        self.day_end = day_end
        self.research_type = research_type
        self.n_samples = n_samples
        self.offset = offset
        self._qrs = self._generate_qrs()


    def get_qrs(self) -> dict:
        return self._qrs


    def _public_fields_digest(self) -> str:
        fields = [str(v) for k, v in self.__dict__.items() if not k.startswith("_")]
        return "".join(fields)


    def _generate_qrs(self, length=16) -> dict:
        random.seed(self._public_fields_digest())
        a_z = string.ascii_lowercase
        new_qrs = {i + 1 + self.offset : ''.join(random.choice(a_z) for _ in range(length)) for i in range(self.n_samples)}
        return new_qrs


    def write_codes(self) -> None:
        if not self._qrs:
            print("No QRs in this research!", file=stderr)
        else:
            research_dir = f"research_{self.research_id}"

            if not os.path.isdir(research_dir):
                os.makedirs(research_dir)

            with open(research_dir + os.sep + f"research={self.research_id}" + f"_qr={self.n_samples}.csv", "w") as f:
                for i in range(self.n_samples):
                    print(f"{i+1+self.offset},{self._qrs[i+1+self.offset]}", file=f)

            print(f"Codes {self.offset+1} to {self.offset+self.n_samples} have been written!", file=stderr)


    def write_pictures(self) -> None:
        if not self._qrs:
            print("No qr codes were generated for this research!", file=stderr)

        else:
            research_dir = f"research_{self.research_id}"

            if not os.path.isdir(research_dir):
                os.makedirs(research_dir)

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
                qr.make_image(fill_color="black", back_color="white").save(research_dir+os.sep+str(n) + ".svg")
            print(f"{self.n_samples} QR images have been written!", file=stderr)



if __name__ == "__main__":
    print("Generating sample research files...")
    new_research = Research(
        research_id=0,
        day_start=1,
        day_end=2,
        research_type=3,
        n_samples=4,
        offset=5
    )

    new_research.write_codes()
    new_research.write_pictures()
