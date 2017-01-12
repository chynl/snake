#include "Console.h"
#include <cstdio>
#include <cstdlib>
#ifdef LINUX_OR_APPLE
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#elif _WIN32
#include <conio.h>
#endif

ConsoleColor::ConsoleColor(const ConsoleColorType foreColor_, const ConsoleColorType backColor_,
                           const bool &foreIntensified_, const bool &backIntensified_)
: foreColor(foreColor_), backColor(backColor_),
foreIntensified(foreIntensified_), backIntensified(backIntensified_) {
}

#ifdef WIN32

WORD Console::setColor(const ConsoleColor &consoleColor) {
    WORD color = 0;
    switch (consoleColor.foreColor) {
        case WHITE:
            color |= FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_BLUE; break;
        case RED:
            color |= FOREGROUND_RED; break;
        case GREEN:
            color |= FOREGROUND_GREEN; break;
        case BLUE:
            color |= FOREGROUND_BLUE; break;
        case YELLOW:
            color |= FOREGROUND_RED | FOREGROUND_GREEN; break;
        case MAGENTA:
            color |= FOREGROUND_BLUE | FOREGROUND_RED; break;
        case CYAN:
            color |= FOREGROUND_BLUE | FOREGROUND_GREEN; break;
        case BLACK:
        default:
            break;
    }
    if (consoleColor.foreIntensified) {
        color |= FOREGROUND_INTENSITY;
    }
    switch (consoleColor.backColor) {
        case WHITE:
            color |= BACKGROUND_GREEN | BACKGROUND_RED | BACKGROUND_BLUE; break;
        case RED:
            color |= BACKGROUND_RED; break;
        case GREEN:
            color |= BACKGROUND_GREEN; break;
        case BLUE:
            color |= BACKGROUND_BLUE; break;
        case YELLOW:
            color |= BACKGROUND_RED | BACKGROUND_GREEN; break;
        case MAGENTA:
            color |= BACKGROUND_BLUE | BACKGROUND_RED; break;
        case CYAN:
            color |= BACKGROUND_BLUE | BACKGROUND_GREEN; break;
        case BLACK:
        default:
            break;
    }
    if (consoleColor.backIntensified) {
        color |= BACKGROUND_INTENSITY;
    }

    // Get origin attribute
    CONSOLE_SCREEN_BUFFER_INFO info;
    HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
    GetConsoleScreenBufferInfo(hStdout, &info);
    WORD originAttr = info.wAttributes;

    // Set new attribute
    HANDLE hout = GetStdHandle(STD_OUTPUT_HANDLE);
    SetConsoleTextAttribute(hout, color);

    // Return the origin attribute
    return originAttr;
}

void Console::resetColor(const WORD &attr) {
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), attr);
}

#endif

void Console::setCursor(const int &x, const int &y) {
#ifdef LINUX_OR_APPLE
    printf("\033[%d;%dH", y + 1, x);  // Param: row and col
#elif _WIN32
    HANDLE hout = GetStdHandle(STD_OUTPUT_HANDLE);
    COORD coord;
    coord.X = x;
    coord.Y = y;
    SetConsoleCursorPosition(hout, coord);
#else
    // Other platforms
#endif
}

void Console::clear() {
#ifdef LINUX_OR_APPLE
    if (system("clear")) {}
#elif _WIN32
    if (system("cls")) {}
#else
    // Other platforms
#endif
}

void Console::write(const std::string &str) {
    printf("%s", str.c_str());
}

void Console::writeWithColor(const std::string &str, const ConsoleColor &consoleColor) {
#ifdef LINUX_OR_APPLE
    int fore = -1, back = -1;
    switch (consoleColor.backColor) {
        case WHITE:
            back = 47; break;
        case RED:
            back = 41; break;
        case GREEN:
            back = 42; break;
        case BLUE:
            back = 44; break;
        case YELLOW:
            back = 43; break;
        case MAGENTA:
            back = 45; break;
        case CYAN:
            back = 46; break;
        case BLACK:
            back = 40; break;
        default:
            break;
    }
    switch (consoleColor.foreColor) {
        case WHITE:
            fore = 37; break;
        case RED:
            fore = 31; break;
        case GREEN:
            fore = 32; break;
        case BLUE:
            fore = 34; break;
        case YELLOW:
            fore = 33; break;
        case MAGENTA:
            fore = 35; break;
        case CYAN:
            fore = 36; break;
        case BLACK:
            fore = 30; break;
        default:
            break;
    }
    if (fore != -1 && back != -1) {
        printf("\033[%d;%dm%s\033[0m", fore, back, str.c_str());
    }
#elif _WIN32
    WORD originAttr = setColor(consoleColor);
    printf("%s", str.c_str());
    resetColor(originAttr);  // Reset to origin output color
#else
    // Other platforms
#endif
}

char Console::getch() {
#ifdef LINUX_OR_APPLE
    struct termios oldattr, newattr;
    int ch;
    tcgetattr(STDIN_FILENO, &oldattr);
    newattr = oldattr;
    newattr.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newattr);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldattr);
    return ch;
#elif _WIN32
    return _getch();
#else
    // Other platforms
#endif
}

int Console::kbhit() {
#ifdef LINUX_OR_APPLE
    struct termios oldt, newt;
    int ch;
    int oldf;

    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);

    ch = getchar();

    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);

    if (ch != EOF) {
        ungetc(ch, stdin);
        return 1;
    }

    return 0;
#elif _WIN32
    return _kbhit();
#else
    // Other platforms
#endif
}
