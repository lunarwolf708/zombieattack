from machine import Pin, I2C
import ssd1306
import main 

# Initialize I2C
i2c = I2C(1, scl=Pin(27), sda=Pin(26))

# Initialize OLED display
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear the display
oled.fill(0)
oled.text("Chris Eats fart", 0, 0)
oled.show()

