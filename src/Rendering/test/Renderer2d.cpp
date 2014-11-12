#include "Renderer2d.h"
#include "gtest/gtest.h"
#include <SDL2/SDL.h>

class RendererTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

    }

    virtual void TearDown()
    {

    }

    Renderer2d _renderer;
};

TEST_F(RendererTest, OpenWindow)
{
    EXPECT_TRUE(_renderer.OpenWindow());
}

int main(int argc, char **argv) {
    SDL_Init(SDL_INIT_VIDEO);

    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}