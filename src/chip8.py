class Chip8:
    __NUM_OF_REGISTERS = 16
    __NUM_OF_KEYS = 16
    __LEVEL_OF_STACK = 16
    __MEM_SIZE = 4096
    __CHIP8_FONTSET = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
            ]

    def __init__(self, win_h, win_w):
        self.opcode = 0x0
        self.memory = [0] * self.__MEM_SIZE
        self.V = [0] * self.__NUM_OF_REGISTERS
        self.IR = 0x0
        self.PC = 0x200
        self.gfx = [0] * (win_h * win_w)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * self.__LEVEL_OF_STACK
        self.sp = 0x0
        self.key = [0] * self.__NUM_OF_KEYS
        self.__load_chip8_font()

    def __load_chip8_font(self):
        for i in range(80):
            self.memory[i] = self.__CHIP8_FONTSET[i]

    def load_ROM(self, program_path):
        with open(program_path, "rb") as f:
            byte = f.read(1)
            i = 512  # 0x200
            while byte:
                if i >= self.__MEM_SIZE and byte:
                    raise Exception("ROM exceed memory capacity of 4KB")
                self.memory[i] = byte[0]
                i += 1
                byte = f.read(1)

    def emulate_cycle(self):
        # Fetch Opcode
        self.opcode = (self.memory[self.PC] << 8) | (self.memory[self.PC + 1])
        # Decode Opcode
        operator = (self.opcode & 0xF000) >> 12
        x_reg = (self.opcode & 0x0F00) >> 8
        y_reg = (self.opcode & 0x00F0) >> 4
        nnn = (self.opcode & 0x0FFF)
        nn = (self.opcode & 0x00FF)
        n = (self.opcode & 0x000F)
        # Execute Opcode
        match operator:
            case 0xA:
                self.IR = nnn
                self.PC += 2
            case _:
                print(f"Unknown Opcode: {self.opcode}")
        # Handle timer
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                print("BEEP!")
