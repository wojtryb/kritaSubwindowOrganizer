from krita import *


class MouseEventHandler:

    def __init__(self, mdi_area) -> None:
        self.mdi_area = mdi_area
        self.last_cursor_position = None
        self.action_was_resize = False

        self.on_press_funs = [self.handle_mouse_button_press]
        self.on_release_funs = [self.handle_mouse_button_release]

    def update_on_event(self, subwin, event):
        if event.type() == QEvent.MouseButtonPress:
            for fun in self.on_press_funs:
                fun(subwin, event)
        elif event.type() == QEvent.MouseButtonRelease:
            for fun in self.on_release_funs:
                fun(subwin, event)

    def handle_mouse_button_press(self, subwin, event):
        local_cursor = event.pos()  # cursor in relation to window
        self.last_cursor_position = self.__map_to_mdi(event)
        self.action_was_resize = (
            -25 < local_cursor.x() < 25
            or -3 < local_cursor.y() < 3
            or subwin.width()-25 < local_cursor.x() < subwin.width()+25
            or subwin.height()-25 < local_cursor.y() < subwin.height()+25
        )

    def handle_mouse_button_release(self, subwin, event):
        self.last_cursor_position = self.__map_to_mdi(event)

    def __map_to_mdi(self, event):
        return self.mdi_area.mapFromGlobal(event.globalPos())
