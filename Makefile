BUILDDIR := build
$(shell mkdir -p $(BUILDDIR))

SRCDIR := src
SRCEXT := cpp
TARGET := $(BUILDDIR)/Snake.out

SRCFILES := $(shell find $(SRCDIR) -type f -name *.$(SRCEXT))
OBJS := $(patsubst $(SRCDIR)/%, $(BUILDDIR)/%, $(SRCFILES:.$(SRCEXT)=.o))

CC := g++ -std=c++11 -Wall -O2

LIB = -pthread

$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) $(LIB)

$(BUILDDIR)/%.o: $(SRCDIR)/%.$(SRCEXT)
	$(CC) -c $< -o $@ 

clean:
	@rm -rf $(BUILDDIR)

run:
	@$(TARGET)

.PHONY: clean run