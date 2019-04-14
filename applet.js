const Applet = imports.ui.applet;
const Util = imports.misc.util;

function MyApplet(orientation, panel_height, instance_id) {
    this._init(orientation, panel_height, instance_id);
}

MyApplet.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _init: function(orientation, panel_height, instance_id) {
        Applet.IconApplet.prototype._init.call(this, orientation, panel_height, instance_id);

        this.set_applet_icon_name("preferences-desktop-display");
        this.set_applet_tooltip(_("Quick switch display arrangements"));
    },

    on_applet_clicked: function() {
        Util.spawn(['bash', '-c', '~/.local/share/cinnamon/applets/display-arrange@sheodox/runquick.sh']);
    }
};

function main(metadata, orientation, panel_height, instance_id) {
    return new MyApplet(orientation, panel_height, instance_id);
}

