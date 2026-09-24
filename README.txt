============================================================
SFM BRING NEAR: LIGHTS
============================================================

Moves selected existing lights into useful starting positions around a model
or prop.

Bring Near does not create lights or finish the lighting for you. You choose
what moves and where it is placed.


------------------------------------------------------------
INSTALLATION
------------------------------------------------------------

1. Extract this ZIP into:

       SourceFilmmaker\game\

2. Restart Source Filmmaker.


------------------------------------------------------------
USAGE
------------------------------------------------------------

1. In the Animation Set Editor, right-click the model or prop you want to
   place lights around.

2. Open:

       Rig > Bring Near...

3. Choose which lights to move.

   Light names can automatically suggest these Placements:

       Key
       Fill
       Backlight
       Rim
       Hair
       Floor
       Eye
       Background

   You can change any suggested Placement from its dropdown.

   Other lights can use:

       Nearby Only

4. Optional:

       Flip Key / Fill / Rim sides

   This places Key, Fill, and Rim on the opposite sides of the model.

5. Click:

       Bring Near

6. Fine-tune the lights normally.

To undo the move, press Ctrl+Z.


------------------------------------------------------------
PLACEMENT NOTES
------------------------------------------------------------

Eye Light places a light close to the model's eyes and points it at them.

Nearby Only moves a light beside the model without changing where it points.

Multiple lights can use the same Placement; Bring Near spaces them apart.

Lights involved in unsupported parent, lock, or other transform relationships
are left unavailable rather than moved unsafely.


------------------------------------------------------------
VERSION NOTES
------------------------------------------------------------

1.0.2
- Added support for SFM Light Kits.
- Light Kits now move as one complete setup centered on the model.

1.0.1
- UI polish and spacing improvements.

1.0.0
- Initial release.


------------------------------------------------------------
TROUBLESHOOTING
------------------------------------------------------------

If Bring Near does not appear under the Rig menu:

1. Confirm the ZIP was extracted into:

       SourceFilmmaker\game\

2. Restart Source Filmmaker.

If a light is unavailable in the prompt chooser, check whether it is locked, parented,
or involved in another transform relationship.


------------------------------------------------------------
UNINSTALL
------------------------------------------------------------

Delete the Bring Near script from:

       SourceFilmmaker\game\usermod\scripts\sfm\animset\

Then restart Source Filmmaker.


------------------------------------------------------------
AUTHOR / LICENSE
------------------------------------------------------------

ChadChan3D
ChadChan3D.com/assets/

CC0 1.0 Universal - Public Domain Dedication
https://creativecommons.org/publicdomain/zero/1.0/
