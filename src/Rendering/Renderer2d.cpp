#include "Renderer2d.h"
#include <SDL2/SDL.h>

Renderer2d::Renderer2d()
{
    
}

bool Renderer2d::OpenWindow()
{
    _window = SDL_CreateWindow(
        "Shiny Ninja",                  // window title
        SDL_WINDOWPOS_UNDEFINED,        // initial x position
        SDL_WINDOWPOS_UNDEFINED,        // initial y position
        640,                            // width, in pixels
        480,                            // height, in pixels
        0                               // flags - see below
    );

    return _window != NULL;
}

bool Renderer2d::CloseWindow()
{
    auto window = _window;
    SDL_DestroyWindow(_window);
    return window != NULL;
}

bool Renderer2d::Render(std::vector<Renderable2d> renderables)
{
    return false;
}
