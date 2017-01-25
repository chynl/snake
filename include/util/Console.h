#ifndef SNAKE_CONSOLE_H_
#define SNAKE_CONSOLE_H_

#include <string>
#if defined(WIN32) || defined(_WIN32)
#include <Windows.h>
#endif

#if defined(__linux__) || defined(__APPLE__)
#define LINUX_OR_APPLE
#endif

enum ConsoleColorType {
    BLACK,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN,
    MAGENTA,
    WHITE,
};

struct ConsoleColor {
    ConsoleColor(const ConsoleColorType foreColor_,
                 const ConsoleColorType backColor_, 
                 const bool foreIntensified_ = false,
                 const bool backIntensified_ = false);
    ConsoleColorType foreColor;
    ConsoleColorType backColor;
    bool foreIntensified;
    bool backIntensified;
};

/*
A cross-platform class to control the output attributes of the console.
*/
class Console {
public:
    /*
    Set console cursor position. The origin is at the left-top corner.
    Axis x extends to the right and axis y extends to the bottom.

    @param x The x coordinate
    @param y The y coordinate
    */
    static void setCursor(const int x = 0, const int y = 0);

    /*
    Clear the console.
    */
    static void clear();

    /*
    Write a string object to console.
    */
    static void write(const std::string &str);

    /*
    Write a string to console with a given color. The intensified
    console color attribute is not supported at the linux platform.
    Reference: http://stackoverflow.com/questions/2616906/how-do-i-output-coloured-text-to-a-linux-terminal
    */
    static void writeWithColor(const std::string &str, const ConsoleColor &consoleColor);

    /*
    A cross-platform getch() method.
    Reference: http://stackoverflow.com/questions/3276546/how-to-implement-getch-function-of-c-in-linux
    */
    static char getch();

    /*
    A cross-platform kbhit() method.
    Reference: http://cboard.cprogramming.com/c-programming/63166-kbhit-linux.html
    */
    static int kbhit();

private:
#ifdef WIN32
    /*
    Set console output color. Only available in windows platform.

    @param color The output color
    @return      The origin console attribute
    */
    static WORD setColor(const ConsoleColor &consoleColor);

    /*
    Reset console output color to default. Only available in windows platform.

    @param attr The console attribute to restore
    */
    static void resetColor(const WORD attr);
#endif
};

#endif
