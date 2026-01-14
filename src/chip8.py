import random


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

    def __init__(self):
        self.draw_flag = False
        self.opcode = 0x0
        self.memory = [0] * self.__MEM_SIZE
        self.V = [0] * self.__NUM_OF_REGISTERS
        self.IR = 0x0
        self.PC = 0x200
        self.gfx = [0] * (64 * 32)
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
            case 0xF:
                match nn:
                    case 0x1E:
                        self.IR = self.IR + self.V[x_reg]
                        self.PC += 2
                    case 0x33:
                        self.memory[self.IR + 0] = (self.V[x_reg] // 100) & 0XFF
                        self.memory[self.IR + 1] = (self.V[x_reg] % 100 // 10) & 0XFF
                        self.memory[self.IR + 2] = (self.V[x_reg] % 10) & 0XFF
                        self.PC += 2
                    case 0x55:
                        for i in range(x_reg + 1):
                            reg_val = self.V[i]
                            self.memory[self.IR + i] = reg_val & 0XFF
                        self.IR += x_reg + 1
                        self.PC += 2
                    case 0x65:
                        for i in range(x_reg + 1):
                            reg_val = self.memory[self.IR + i]
                            self.V[i] = reg_val
                        self.IR += x_reg + 1
                        self.PC += 2
                    case 0x0A:
                        key_pressed = False
                        for i in range(self.__NUM_OF_KEYS):
                            if self.key[i]:
                                self.V[x_reg] = i
                                key_pressed = True
                                break
                        if not key_pressed:
                            return
                        self.PC += 2
                    case 0x07:
                        self.V[x_reg] = self.delay_timer & 0xFF
                        self.PC += 2
                    case 0x15:
                        self.delay_timer = self.V[x_reg]
                        self.PC += 2
                    case 0x18:
                        self.sound_timer = self.V[x_reg]
                        self.PC += 2
                    case 0x29:
                        self.IR = self.V[x_reg] * 0x5
                        self.PC += 2
            case 0xE:
                match nn:
                    case 0x9E:
                        if self.key[self.V[x_reg]]:
                            self.PC += 4
                        else:
                            self.PC += 2
                    case 0xA1:
                        if not self.key[self.V[x_reg]]:
                            self.PC += 4
                        else:
                            self.PC += 2
            case 0xB:
                addr = nnn + self.V[0]
                self.PC = addr
            case 0xC:
                self.V[x_reg] = random.randint(0, 255) & nn
                self.PC += 2
            case 0xD:
                self.V[0xF] = 0
                for row in range(n):
                    pixel = self.memory[self.IR + row]
                    for col in range(8):
                        x_coord = (self.V[x_reg] + col)
                        y_coord = (self.V[y_reg] + row)
                        # If the pixel exist in memory, render the pixel
                        if 0 <= x_coord < 64 and 0 <= y_coord < 32:
                            if pixel & (0x80 >> col):
                                # If the pixel is in the display, set VF for collision detection
                                pix_loc = x_coord + (y_coord * 64)
                                if self.gfx[pix_loc]:
                                    self.V[0xF] = 1
                                self.gfx[pix_loc] ^= 1
                self.draw_flag = True
                self.PC += 2
            case 0x0:
                match nnn:
                    case 0x0EE:
                        self.sp -= 1
                        self.PC = self.stack[self.sp]
                        self.PC += 2
                    case 0x0E0:
                        self.gfx = [0 for _ in self.gfx]
                        self.PC += 2
            case 0x1:
                self.PC = nnn
            case 0x2:
                self.stack[self.sp] = self.PC + 2
                self.sp += 1
                self.PC = nnn
            case 0x3:
                if self.V[x_reg] == nn:
                    self.PC += 4
                else:
                    self.PC += 2
            case 0x4:
                if self.V[x_reg] != nn:
                    self.PC += 4
                else:
                    self.PC += 2
            case 0x5:
                if self.V[x_reg] == self.V[y_reg]:
                    self.PC += 4
                else:
                    self.PC += 2
            case 0x9:
                if self.V[x_reg] != self.V[y_reg]:
                    self.PC += 4
                else:
                    self.PC += 2
            case 0x6:
                self.V[x_reg] = nn
                self.PC += 2
            case 0x7:
                self.V[x_reg] = (self.V[x_reg] + nn) & 0xFF
                self.PC += 2
            case 0x8:
                match n:
                    case 0x0:
                        self.V[x_reg] = self.V[y_reg]
                        self.PC += 2
                    case 0x1:
                        self.V[x_reg] = self.V[x_reg] | self.V[y_reg]
                        self.PC += 2
                    case 0x2:
                        self.V[x_reg] = self.V[x_reg] & self.V[y_reg]
                        self.PC += 2
                    case 0x3:
                        self.V[x_reg] = self.V[x_reg] ^ self.V[y_reg]
                        self.PC += 2
                    case 0x4:
                        sum_xy = self.V[x_reg] + self.V[y_reg]
                        if sum_xy > 0xFF:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        self.V[x_reg] = sum_xy & 0xFF
                        self.PC += 2
                    case 0x5:
                        if self.V[x_reg] >= self.V[y_reg]:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        self.V[x_reg] = (self.V[x_reg] - self.V[y_reg]) & 0xFF
                        self.PC += 2
                    case 0x7:
                        if self.V[y_reg] >= self.V[x_reg]:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        self.V[x_reg] = (self.V[y_reg] - self.V[x_reg]) & 0xFF
                        self.PC += 2
                    case 0x6:
                        self.V[x_reg] = self.V[y_reg]
                        self.V[0xF] = self.V[x_reg] & 0x1
                        self.V[x_reg] = self.V[x_reg] >> 1
                        self.PC += 2
                    case 0xE:
                        self.V[x_reg] = self.V[y_reg]
                        self.V[0xF] = (self.V[x_reg] & 0x80) >> 7
                        self.V[x_reg] = (self.V[x_reg] << 1) & 0xFF
                        self.PC += 2
            case _:
                print(f"Unknown Opcode: {self.opcode}")

        # Handle timer
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
