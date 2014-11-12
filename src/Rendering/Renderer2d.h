#ifndef RENDERER2D_H
#define RENDERER2D_H

#include <vector>
#include "Renderable2d.h"
#include "SDL2/SDL.h"

class Renderer2d
{
public:
    Renderer2d();
    bool OpenWindow();
    bool CloseWindow();
    bool Render(std::vector<Renderable2d>);
private:
    SDL_Window *_window;
};

#endif
