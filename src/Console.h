#pragma once

#include <string>
#if defined(WIN32) || defined(_WIN32)
#include <Windows.h>
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
    ConsoleColor(const ConsoleColorType foreColor_, const ConsoleColorType backColor_, 
                 const bool &foreIntensified_ = false, const bool &backIntensified_ = false);
    ConsoleColorType foreColor;
    ConsoleColorType backColor;
    bool foreIntensified;
    bool backIntensified;
};

/*
A cross-platform class to control the output attributes of the console/terminal.
*/
class Console {
public:
    /*
    Set console cursor position.
    The origin is at the left-top corner. Axis x extends to the right
    and axis y extends to the bottom.

    @param console x coordinate
    @param console y coordinate
    */
    static void setCursor(const int &x = 0, const int &y = 0);

    /*
    Clear the console.
    */
    static void clear();

    /*
    Write string to console

    @param str the string to write
    */
    static void write(const std::string &str);

    /*
    Write string to console with a given color.
    In linux platform, the intensified console color
    attribute is not supported.
    Reference:
    1. http://stackoverflow.com/questions/2616906/how-do-i-output-coloured-text-to-a-linux-terminal

    @param str the string to write
    @param color the output color
    */
    static void writeWithColor(const std::string &str, const ConsoleColor &consoleColor);

    /*
    A cross-platform getch() method.
    Reference:
    1. http://stackoverflow.com/questions/3276546/how-to-implement-getch-function-of-c-in-linux
    */
    static char getch();

    /*
    A cross-platform kbhit() method.
    Reference:
    1. http://cboard.cprogramming.com/c-programming/63166-kbhit-linux.html
    */
    static int kbhit();

private:
#ifdef WIN32
    /*
    Set console output color.
    Only available in windows platform.

    @param color the output color
    @return the origin console attribute
    */
    static WORD setColor(const ConsoleColor &consoleColor);

    /*
    Reset console output color to default.
    Only available in windows platform.

    @param attr the console attribute to restore
    */
    static void resetColor(const WORD &attr);
#endif
};
