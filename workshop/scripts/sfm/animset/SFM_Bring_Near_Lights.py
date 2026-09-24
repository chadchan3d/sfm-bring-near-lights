# -*- coding: utf-8 -*-
r"""
SFM Bring Near: Lights
T55 — current v1.01 visual base + native Light Kit support.
"""

import re
import math
import base64
import traceback

import sfm
import sfmApp
import vs
from vs import movieobjects, studio, datamodel
from PySide import QtGui, QtCore

MAX_BONES = 1024
MAX_ATTACHMENTS = 256
MAX_PARENT_CHAIN = 64
MAX_REFERENCES_PER_LIGHT = 512
MAX_TOTAL_REFERENCES_PER_INVENTORY = 4096
MAX_ANIMATION_SETS_IN_SHOT = 4096
MAX_PROJECTED_LIGHTS_IN_SHOT = 256

EPS = 1.0e-8
VERIFY_POS_EPS = 0.05
NOOP_POS_EPS = 0.01
NOOP_ANG_DEG = 0.05
MIN_AIM_DOT = 0.9990

FALLBACK_NEARBY_SCALE = 18.0
PROP_T_FROM_MEDIAN_DIM = 0.25
MAX_PROP_BOUND_DIM = 100000.0
EYE_DISTANCE = 6.0

BODY_FAMILIES = (
    (
        "ValveBiped",
        (
            "ValveBiped.Bip01_L_Thigh",
            "ValveBiped.Bip01_R_Thigh",
            "ValveBiped.Bip01_L_Clavicle",
            "ValveBiped.Bip01_R_Clavicle",
        ),
    ),
    (
        "bip",
        (
            "bip_hip_L",
            "bip_hip_R",
            "bip_collar_L",
            "bip_collar_R",
        ),
    ),
)

VALIDATED_EYE_PARENT_BONES = (
    "ValveBiped.Bip01_Head1",
    "bip_head",
)

ROLE_KEY = "Key Light"
ROLE_FILL = "Fill Light"
ROLE_BACK = "Backlight"
ROLE_RIM = "Rim Light"
ROLE_HAIR = "Hair Light"
ROLE_BACKGROUND = "Background Light"
ROLE_FLOOR = "Floor Light"
ROLE_EYE = "Eye Light"
ROLE_NEARBY = "Nearby Only"
ROLE_LIGHT_KIT = "__LIGHT_KIT__"

ROLE_ORDER = (
    ROLE_KEY,
    ROLE_FILL,
    ROLE_BACK,
    ROLE_RIM,
    ROLE_HAIR,
    ROLE_FLOOR,
    ROLE_EYE,
    ROLE_BACKGROUND,
    ROLE_NEARBY,
)

BODY_ROLES = (
    ROLE_KEY,
    ROLE_FILL,
    ROLE_BACK,
    ROLE_RIM,
    ROLE_HAIR,
    ROLE_BACKGROUND,
    ROLE_FLOOR,
)

ROLE_DESCRIPTIONS = {
    ROLE_KEY:
        "In front and above the model's right side; points toward the upper chest and neck.",
    ROLE_FILL:
        "In front, opposite Key Light, positioned lower; points toward the upper chest and neck.",
    ROLE_BACK:
        "Behind and above the model; points toward the head and shoulders.",
    ROLE_RIM:
        "Above and behind the model's right side; points toward the upper body.",
    ROLE_HAIR:
        "Almost directly above, slightly behind; points toward the head.",
    ROLE_FLOOR:
        "Almost directly below, slightly in front; points up toward the torso.",
    ROLE_EYE:
        "Very close in front of eyes; points toward the eyes.",
    ROLE_BACKGROUND:
        "Above the model; points toward the area behind the model.",
    ROLE_NEARBY:
        "Beside the model; keeps the current direction.",
}

BODY_ROLE_OFFSETS = {
    ROLE_KEY:        ( 3.20,  3.35,  2.55),
    ROLE_FILL:       ( 3.00, -3.35,  1.35),
    ROLE_BACK:       (-4.20,  0.00,  1.20),
    ROLE_RIM:        (-5.60,  5.20,  1.00),
    ROLE_HAIR:       (-0.60,  0.00,  4.00),
    ROLE_BACKGROUND: ( 0.25,  0.00,  2.40),
    ROLE_FLOOR:      ( 0.60,  0.00, -4.95),
}

UI_TITLE = "Bring Near: Lights"
WINDOW_ICON_PNG_B64 = (
    "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"
    "RK5CYII="
)
WINDOW_ICON_CACHE = None
UI_TOP = "Choose which lights to move and where to place them around this model."
MSG_NO_LIGHTS = "No lights were found in this shot."
MSG_SELECT_LIGHT = "Select at least one light to move."
MSG_NOOP = "No changes needed. These lights are already at their Bring Near positions."
MSG_OPEN_FAIL = "Bring Near could not open. Try again."
MSG_MOVE_FAIL = "Bring Near could not move the selected lights. Nothing was moved. Try again."
MSG_CONTEXT_FAIL = (
    "Bring Near cannot continue in the current shot. Nothing was moved. "
    "Run Bring Near again."
)
MSG_LOCK_FAIL = (
    "A selected light's relationships changed, so nothing was moved. "
    "Close Bring Near and run Bring Near again."
)
MSG_PARTIAL = (
    "Bring Near could not complete or verify the move.\n"
    "Press Ctrl+Z to undo it."
)
LOCK_INBOUND_TEXT = "Locked to another object."
LOCK_OUTBOUND_TEXT = "Another object is locked to this light."
CHILD_OUTBOUND_TEXT = "Another object is parented to this light."
LOCK_UNKNOWN_TEXT = "Cannot verify this light's relationships."

LOCK_INBOUND_HELP = (
    "Close Bring Near, unlock this light in the Animation Set Editor, "
    "then run Bring Near again."
)
LOCK_OUTBOUND_HELP = (
    "Close Bring Near, remove the dependent object's lock to this light, "
    "then run Bring Near again."
)
CHILD_OUTBOUND_HELP = (
    "Close Bring Near, remove the object's parent relationship to this light, "
    "then run Bring Near again."
)
LOCK_UNKNOWN_HELP = (
    "Bring Near cannot verify this light's relationships, so it will not move it."
)
EYE_HELP = "Eye Light needs a model with eyes Bring Near can locate."
BODY_HELP = (
    "This model does not provide a clear front, sides, and height. "
    "Nearby Only is still available."
)

LIGHT_KIT_PLACEMENT_TEXT = "Whole kit centered on model"
LIGHT_KIT_BODY_TEXT = "Needs a character model."
LIGHT_KIT_EXTERNAL_TEXT = "Another object is parented to this lighting setup."
LIGHT_KIT_UNKNOWN_TEXT = "Cannot safely move this lighting setup."

HELP_LICENSE = u"License: CC0 \u00b7 Author: ChadChan3D"


HELP_INTRO_1 = (
    "Bring Near gathers selected lights and puts them in starting positions "
    "around this model or prop."
)

HELP_TABLE = (
    (ROLE_KEY,        "In front and above the model's right side",          "Upper chest / neck"),
    (ROLE_FILL,       "In front, opposite Key Light, positioned lower",     "Upper chest / neck"),
    (ROLE_BACK,       "Behind and above the model",            "Head and shoulders"),
    (ROLE_RIM,        "Above and behind the model's right side",            "Upper body"),
    (ROLE_HAIR,       "Almost directly above, slightly behind","Head"),
    (ROLE_FLOOR,      "Almost directly below, slightly in front", "Up toward torso"),
    (ROLE_EYE,        "Very close in front of eyes",           "Eyes"),
    (ROLE_BACKGROUND, "Above the model",                       "Area behind model"),
    (ROLE_NEARBY,     "Beside the model",                     "Keeps current direction"),
)

HELP_DUPLICATES = (
    "Multiple lights can use the same Placement; Bring Near spaces them apart."
)

HELP_BOTTOM = (
    "These are practical starting positions based on common lighting roles, "
    "not rules for how a shot should be lit."
)


# ---------------------------------------------------------------------------
# Logging and identities
# ---------------------------------------------------------------------------

def _u(v):
    """
    Convert SFM/Python-2 text to Unicode without exposing repr escapes.

    SFM on Windows can return narrow byte strings for animation-set names.
    Prefer UTF-8 when the bytes are valid UTF-8, then the active Windows ANSI
    code page, then CP1252/Latin-1 as conservative Western fallbacks.
    """
    try:
        if isinstance(v, unicode):
            return v
    except Exception:
        pass

    try:
        if isinstance(v, str):
            for encoding in ("utf-8", "mbcs", "cp1252", "latin-1"):
                try:
                    return v.decode(encoding)
                except Exception:
                    pass
            return v.decode("latin-1", "replace")
    except Exception:
        pass

    try:
        return unicode(v)
    except Exception:
        return u"<unprintable>"


def _identity(obj):
    d = {"id": None, "handle": None, "name": None}
    if obj is None:
        return d
    for key, meth in (("id", "GetId"), ("handle", "GetHandle"), ("name", "GetName")):
        try:
            d[key] = _u(getattr(obj, meth)())
        except Exception:
            pass
    return d


def _same(a, b):
    if a is None or b is None:
        return False

    ia = _identity(a)
    ib = _identity(b)

    if ia["id"] is not None and ib["id"] is not None:
        return ia["id"] == ib["id"]

    if ia["handle"] is not None and ib["handle"] is not None:
        return ia["handle"] == ib["handle"]

    try:
        return a == b
    except Exception:
        return a is b


def _array(obj, attr_name):
    try:
        arr = getattr(obj, attr_name)
        return [arr[i] for i in range(len(arr))]
    except Exception:
        return []


def _required_id(obj, label):
    ident = _identity(obj)
    value = ident["id"]

    if value is None:
        raise RuntimeError("%s identity unavailable" % label)

    return value


def _array_required(obj, attr_name, label):
    try:
        arr = getattr(obj, attr_name)
        count = len(arr)
        return [arr[i] for i in range(count)]
    except Exception:
        raise RuntimeError("%s could not be read" % label)


def _shot_animation_sets_bounded(shot):
    try:
        arr = shot.animationSets
        count = len(arr)
    except Exception:
        raise RuntimeError("shot animation sets could not be read")

    if count < 0 or count > MAX_ANIMATION_SETS_IN_SHOT:
        raise RuntimeError("shot animation-set limit")

    return [arr[i] for i in range(count)]


def _timeline_snapshot():
    try:
        has_document = bool(sfmApp.HasDocument())
    except Exception:
        raise RuntimeError("document state unavailable")

    if not has_document:
        raise RuntimeError("no open document")

    try:
        document_root = sfmApp.GetDocumentRoot()
    except Exception:
        raise RuntimeError("document root unavailable")

    if document_root is None:
        raise RuntimeError("document root unavailable")

    try:
        mode = sfmApp.GetTimelineMode()
        mode_name = _u(sfmApp.GetNameForTimelineMode(mode))
        head_frames = float(sfmApp.GetHeadTimeInFrames())
        head_seconds = float(sfmApp.GetHeadTimeInSeconds())
        live_shot = sfmApp.GetShotAtCurrentTime()
    except Exception:
        raise RuntimeError("timeline context unavailable")

    if not _finite_number(head_frames) or not _finite_number(head_seconds):
        raise RuntimeError("timeline head is invalid")

    return {
        "document_root": document_root,
        "document_id": _required_id(document_root, "document root"),
        "mode": mode,
        "mode_name": mode_name,
        "head_frames": head_frames,
        "head_seconds": head_seconds,
        "live_shot": live_shot,
        "live_shot_id": (
            _required_id(live_shot, "live shot")
            if live_shot is not None else None
        ),
    }


def _same_timeline_context(before, after):
    if before["document_id"] != after["document_id"]:
        return False, "document changed"

    if before["mode"] != after["mode"]:
        return False, "timeline mode changed"

    if before["mode_name"] != after["mode_name"]:
        return False, "timeline mode name changed"

    if before["live_shot_id"] != after["live_shot_id"]:
        return False, "live shot changed"

    if abs(before["head_frames"] - after["head_frames"]) > 0.001:
        return False, "playhead frame changed"

    if abs(before["head_seconds"] - after["head_seconds"]) > 0.0001:
        return False, "playhead time changed"

    return True, None


def _optional_parent_state(dag):
    try:
        parent = dag.GetParent()
    except Exception:
        return {
            "complete": False,
            "present": None,
            "id": None,
            "parent": None,
        }

    if parent is None:
        return {
            "complete": True,
            "present": False,
            "id": None,
            "parent": None,
        }

    try:
        parent_id = _required_id(parent, "parent")
    except Exception:
        return {
            "complete": False,
            "present": True,
            "id": None,
            "parent": parent,
        }

    return {
        "complete": True,
        "present": True,
        "id": parent_id,
        "parent": parent,
    }


def _same_optional_parent(a, b):
    if not a["complete"] or not b["complete"]:
        return False

    if a["present"] != b["present"]:
        return False

    if not a["present"]:
        return True

    return a["id"] == b["id"]


# ---------------------------------------------------------------------------
# User-facing dialogs
# ---------------------------------------------------------------------------

def _window_icon():
    global WINDOW_ICON_CACHE

    if WINDOW_ICON_CACHE is not None:
        return WINDOW_ICON_CACHE

    try:
        payload = base64.b64decode(WINDOW_ICON_PNG_B64)
        pixmap = QtGui.QPixmap()

        if pixmap.loadFromData(payload, "PNG"):
            WINDOW_ICON_CACHE = QtGui.QIcon(pixmap)
        else:
            WINDOW_ICON_CACHE = QtGui.QIcon()
    except Exception:
        WINDOW_ICON_CACHE = QtGui.QIcon()

    return WINDOW_ICON_CACHE


def _apply_window_icon(widget):
    try:
        icon = _window_icon()

        if icon is not None and not icon.isNull():
            widget.setWindowIcon(icon)
    except Exception:
        pass


def _active_window():
    try:
        app = QtGui.QApplication.instance()

        if app is not None:
            candidate = app.activeWindow()

            # SFM/PySide can occasionally expose an active QObject that is not
            # a QWidget. QDialog/QMessageBox native constructors reject that
            # object as a parent. A parent is optional, so fail safely to None.
            if candidate is not None and isinstance(candidate, QtGui.QWidget):
                return candidate
    except Exception:
        pass

    return None


def _show_message(text, icon_kind):
    try:
        box = QtGui.QMessageBox(_active_window())
        box.setWindowTitle(UI_TITLE)
        box.setText(text)
        box.setIcon(icon_kind)
        box.setStandardButtons(QtGui.QMessageBox.Ok)
        _apply_window_icon(box)
        box.exec_()
    except Exception:
        pass


def _show_info(text):
    _show_message(text, QtGui.QMessageBox.Information)


def _show_warning(text):
    _show_message(text, QtGui.QMessageBox.Warning)


# ---------------------------------------------------------------------------
# Bounded vector/quaternion math
# ---------------------------------------------------------------------------

def _finite_number(v):
    try:
        f = float(v)
    except Exception:
        return False

    try:
        return not math.isnan(f) and not math.isinf(f)
    except Exception:
        return False


def _require_finite_tuple(values, label):
    out = tuple(float(v) for v in values)

    if not all(_finite_number(v) for v in out):
        raise RuntimeError("%s contains non-finite values" % label)

    return out


def _vec3(v):
    return _require_finite_tuple(
        (v.x, v.y, v.z),
        "vector"
    )


def _quat4(q):
    return _require_finite_tuple(
        (q.x, q.y, q.z, q.w),
        "quaternion"
    )


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(v, s):
    return (v[0] * s, v[1] * s, v[2] * s)


def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def _cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def _norm(v):
    v = _require_finite_tuple(v, "vector")
    n2 = _dot(v, v)

    if not _finite_number(n2) or n2 < 0.0:
        raise RuntimeError("invalid vector norm")

    n = math.sqrt(n2)

    if not _finite_number(n):
        raise RuntimeError("invalid vector norm")

    return n


def _normalize(v):
    v = _require_finite_tuple(v, "vector")
    n = _norm(v)

    if n <= EPS:
        raise RuntimeError("degenerate vector")

    return _require_finite_tuple(
        _scale(v, 1.0 / n),
        "normalized vector"
    )


def _mid(a, b):
    return _scale(_add(a, b), 0.5)


def _distance(a, b):
    return _norm(_sub(a, b))


def _qnorm(q):
    return math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3])


def _qangle_deg(a, b):
    a = _require_finite_tuple(a, "quaternion A")
    b = _require_finite_tuple(b, "quaternion B")

    na = _qnorm(a)
    nb = _qnorm(b)

    if not _finite_number(na) or not _finite_number(nb):
        raise RuntimeError("invalid quaternion norm")

    if na <= EPS or nb <= EPS:
        raise RuntimeError("degenerate quaternion")

    d = abs(
        (a[0]*b[0] + a[1]*b[1] + a[2]*b[2] + a[3]*b[3]) /
        (na * nb)
    )

    if not _finite_number(d):
        raise RuntimeError("invalid quaternion comparison")

    d = max(0.0, min(1.0, d))
    result = math.degrees(2.0 * math.acos(d))

    if not _finite_number(result):
        raise RuntimeError("invalid quaternion angle")

    return result


def _quat_from_basis(x_axis, y_axis, z_axis):
    m00, m10, m20 = x_axis
    m01, m11, m21 = y_axis
    m02, m12, m22 = z_axis

    trace = m00 + m11 + m22

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * s
        qx = (m21 - m12) / s
        qy = (m02 - m20) / s
        qz = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        qw = (m21 - m12) / s
        qx = 0.25 * s
        qy = (m01 + m10) / s
        qz = (m02 + m20) / s
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        qw = (m02 - m20) / s
        qx = (m01 + m10) / s
        qy = 0.25 * s
        qz = (m12 + m21) / s
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
        qw = (m10 - m01) / s
        qx = (m02 + m20) / s
        qy = (m12 + m21) / s
        qz = 0.25 * s

    raw_q = _require_finite_tuple(
        (qx, qy, qz, qw),
        "basis quaternion"
    )

    qn = math.sqrt(
        raw_q[0]*raw_q[0] +
        raw_q[1]*raw_q[1] +
        raw_q[2]*raw_q[2] +
        raw_q[3]*raw_q[3]
    )

    if not _finite_number(qn) or qn <= EPS:
        raise RuntimeError("zero or invalid quaternion")

    normalized = _require_finite_tuple(
        (
            raw_q[0] / qn,
            raw_q[1] / qn,
            raw_q[2] / qn,
            raw_q[3] / qn,
        ),
        "normalized quaternion"
    )

    return vs.Quaternion(
        normalized[0],
        normalized[1],
        normalized[2],
        normalized[3]
    )


def _axes_from_quaternion(q):
    qa = vs.QAngle()
    vs.mathlib.QuaternionAngles(q, qa)

    f = vs.Vector(0, 0, 0)
    r = vs.Vector(0, 0, 0)
    u = vs.Vector(0, 0, 0)
    vs.mathlib.AngleVectors(qa, f, r, u)

    # Source AngleVectors returns forward=local +X, right=local -Y, up=local +Z.
    x_axis = _normalize(_vec3(f))
    y_axis = _scale(_normalize(_vec3(r)), -1.0)
    z_axis = _normalize(_vec3(u))

    return qa, x_axis, y_axis, z_axis


def _rotate_xyz_for_quaternion(q):
    qa, _, _, _ = _axes_from_quaternion(q)

    # Empirically validated mapping:
    # sfm.Rotate(X,Y,Z) = (roll,pitch,yaw).
    return (float(qa.z), float(qa.x), float(qa.y))


def _validate_orthogonal_axes(a, b, c, handedness, label):
    a = _normalize(a)
    b = _normalize(b)
    c = _normalize(c)

    if abs(_dot(a, b)) > 0.01:
        raise RuntimeError("%s axes A/B not orthogonal" % label)
    if abs(_dot(a, c)) > 0.01:
        raise RuntimeError("%s axes A/C not orthogonal" % label)
    if abs(_dot(b, c)) > 0.01:
        raise RuntimeError("%s axes B/C not orthogonal" % label)

    h = _dot(_normalize(_cross(a, b)), c)

    if handedness == "positive":
        if h < 0.99:
            raise RuntimeError("%s frame handedness invalid" % label)
    elif handedness == "negative":
        if h > -0.99:
            raise RuntimeError("%s frame handedness invalid" % label)
    else:
        raise RuntimeError("unknown handedness contract")

    return a, b, c


def _aim_quaternion(dest, target, stable_up):
    aim_x = _normalize(_sub(target, dest))

    aim_z = _sub(stable_up, _scale(aim_x, _dot(stable_up, aim_x)))
    aim_z = _normalize(aim_z)

    aim_y = _normalize(_cross(aim_z, aim_x))
    aim_z = _normalize(_cross(aim_x, aim_y))

    q = _quat_from_basis(aim_x, aim_y, aim_z)

    _, check_x, _, check_z = _axes_from_quaternion(q)

    if _dot(check_x, aim_x) < MIN_AIM_DOT:
        raise RuntimeError("aim forward preflight failed")

    if _dot(check_z, aim_z) < MIN_AIM_DOT:
        raise RuntimeError("aim up preflight failed")

    return q


# ---------------------------------------------------------------------------
# Projected-light discovery
# ---------------------------------------------------------------------------

def _resolve_projected_light(aset):
    try:
        obj = aset.light
    except Exception:
        return None

    if obj is None:
        return None

    try:
        if not obj.IsA("DmeProjectedLight"):
            return None
        dag = movieobjects.CastElementAsDmeDag(obj)
    except Exception:
        return None

    if dag is None:
        return None

    try:
        ctrl = aset.FindTransformControl(dag)
    except Exception:
        return None

    if ctrl is None:
        return None

    try:
        if not _same(ctrl.GetDag(), dag):
            return None
    except Exception:
        return None

    try:
        transform = ctrl.GetTransform()
    except Exception:
        return None

    if transform is None:
        return None

    try:
        transform_dag = transform.GetDag()
    except Exception:
        return None

    if transform_dag is None or not _same(transform_dag, dag):
        return None

    try:
        _required_id(aset, "light animation set")
        _required_id(dag, "light DAG")
        _required_id(ctrl, "light transform control")
        _required_id(transform, "light transform")
    except Exception:
        return None

    return dag, ctrl, transform


def _reverse_override_state(dag, total_budget):
    """
    Bounded direct-reference scan.

    A positive overrideParent reference is sufficient to BLOCK immediately.
    To classify a light FREE, the scan must reach the native end sentinel
    without a read failure or budget exhaustion.
    """
    result = {
        "complete": False,
        "outbound": False,
        "owner": None,
        "visited": 0,
        "error": None,
    }

    try:
        dm = datamodel.g_pDataModel
        token = dm.FirstAttributeReferencingElement(dag.GetHandle())
    except Exception:
        result["error"] = u"reference scan could not start"
        return result

    seen = set()

    try:
        while token != 0:
            if token in seen:
                raise RuntimeError("reference iterator cycle")

            if len(seen) >= MAX_REFERENCES_PER_LIGHT:
                raise RuntimeError("per-light reference limit")

            if total_budget[0] >= MAX_TOTAL_REFERENCES_PER_INVENTORY:
                raise RuntimeError("inventory reference limit")

            seen.add(token)
            result["visited"] += 1
            total_budget[0] += 1

            attr = dm.GetAttributeFromIterator(token)
            if attr is None:
                raise RuntimeError("reference attribute unreadable")

            name = _u(attr.GetName())

            if name == u"overrideParent":
                owner = attr.GetOwner()
                if owner is None:
                    raise RuntimeError("overrideParent owner unreadable")

                result["outbound"] = True
                result["owner"] = owner
                result["complete"] = True
                return result

            token = dm.NextAttributeReferencingElement(token)

        result["complete"] = True

    except Exception:
        result["error"] = _u(traceback.format_exc())

    return result


def _direct_child_state(dag):
    """
    A light with ordinary DAG children can move collateral content.
    Normal projected lights previously qualified with zero direct children.
    """
    result = {
        "complete": False,
        "has_children": False,
        "child_count": 0,
        "first_child": None,
        "error": None,
    }

    try:
        children = dag.GetAttribute("children")
        if children is None:
            raise RuntimeError("children attribute unavailable")

        count = len(children)
        result["child_count"] = count

        if count > 0:
            result["has_children"] = True
            result["first_child"] = children[0]

        result["complete"] = True
    except Exception:
        result["error"] = _u(traceback.format_exc())

    return result


def _light_eligibility(dag, total_budget):
    """
    Return one of:
        ELIGIBLE
        BLOCKED_CHILD_OUTBOUND
        BLOCKED_INBOUND
        BLOCKED_OUTBOUND
        UNKNOWN

    Any unreadable relationship evidence fails closed.
    """
    direct_children = _direct_child_state(dag)

    if not direct_children["complete"]:
        return {
            "state": "UNKNOWN",
            "reason_text": LOCK_UNKNOWN_TEXT,
            "reason_help": LOCK_UNKNOWN_HELP,
            "owner": None,
            "reference_visits": 0,
            "direct_child_count": direct_children["child_count"],
        }

    if direct_children["has_children"]:
        return {
            "state": "BLOCKED_CHILD_OUTBOUND",
            "reason_text": CHILD_OUTBOUND_TEXT,
            "reason_help": CHILD_OUTBOUND_HELP,
            "owner": direct_children["first_child"],
            "reference_visits": 0,
            "direct_child_count": direct_children["child_count"],
        }

    # Stored inbound override relation. The True overload exposes retained
    # parent state even when participation is disabled.
    try:
        stored_parent = dag.GetOverrideParent(True)
    except Exception:
        return {
            "state": "UNKNOWN",
            "reason_text": LOCK_UNKNOWN_TEXT,
            "reason_help": LOCK_UNKNOWN_HELP,
            "owner": None,
            "reference_visits": 0,
            "direct_child_count": 0,
        }

    if stored_parent is not None:
        return {
            "state": "BLOCKED_INBOUND",
            "reason_text": LOCK_INBOUND_TEXT,
            "reason_help": LOCK_INBOUND_HELP,
            "owner": stored_parent,
            "reference_visits": 0,
            "direct_child_count": 0,
        }

    reverse = _reverse_override_state(dag, total_budget)

    if reverse["outbound"]:
        return {
            "state": "BLOCKED_OUTBOUND",
            "reason_text": LOCK_OUTBOUND_TEXT,
            "reason_help": LOCK_OUTBOUND_HELP,
            "owner": reverse["owner"],
            "reference_visits": reverse["visited"],
            "direct_child_count": 0,
        }

    if not reverse["complete"]:
        return {
            "state": "UNKNOWN",
            "reason_text": LOCK_UNKNOWN_TEXT,
            "reason_help": LOCK_UNKNOWN_HELP,
            "owner": None,
            "reference_visits": reverse["visited"],
            "direct_child_count": 0,
        }

    return {
        "state": "ELIGIBLE",
        "reason_text": None,
        "reason_help": None,
        "owner": None,
        "reference_visits": reverse["visited"],
        "direct_child_count": 0,
    }


def _light_kit_root_eligibility(dag, total_budget):
    try:
        stored_parent = dag.GetOverrideParent(True)
    except Exception:
        return {
            "state": "UNKNOWN",
            "reason_text": LIGHT_KIT_UNKNOWN_TEXT,
            "reason_help": None,
            "owner": None,
            "reference_visits": 0,
            "direct_child_count": 0,
        }

    if stored_parent is not None:
        return {
            "state": "BLOCKED_INBOUND",
            "reason_text": LOCK_INBOUND_TEXT,
            "reason_help": None,
            "owner": stored_parent,
            "reference_visits": 0,
            "direct_child_count": 0,
        }

    reverse = _reverse_override_state(dag, total_budget)

    if reverse["outbound"]:
        return {
            "state": "BLOCKED_OUTBOUND",
            "reason_text": LOCK_OUTBOUND_TEXT,
            "reason_help": None,
            "owner": reverse["owner"],
            "reference_visits": reverse["visited"],
            "direct_child_count": 0,
        }

    if not reverse["complete"]:
        return {
            "state": "UNKNOWN",
            "reason_text": LIGHT_KIT_UNKNOWN_TEXT,
            "reason_help": None,
            "owner": None,
            "reference_visits": reverse["visited"],
            "direct_child_count": 0,
        }

    return {
        "state": "ELIGIBLE",
        "reason_text": None,
        "reason_help": None,
        "owner": None,
        "reference_visits": reverse["visited"],
        "direct_child_count": 0,
    }


def _natural_name_key(name):
    parts = re.split(u"([0-9]+)", _u(name).lower())
    key = []

    for part in parts:
        if not part:
            continue

        if re.match(u"^[0-9]+$", part):
            key.append((1, int(part)))
        else:
            key.append((0, part))

    return tuple(key)


def _inventory_lights(shot, total_budget=None):
    rows = []

    if total_budget is None:
        total_budget = [0]

    for aset in _shot_animation_sets_bounded(shot):
        pair = _resolve_projected_light(aset)
        if pair is None:
            continue

        if len(rows) >= MAX_PROJECTED_LIGHTS_IN_SHOT:
            raise RuntimeError("projected-light inventory limit")

        dag, ctrl, transform = pair

        try:
            name = _u(aset.GetName())
        except Exception:
            name = u"Light"

        eligibility = _light_eligibility(dag, total_budget)
        locked = (eligibility["state"] != "ELIGIBLE")

        rows.append({
            "kind": "LIGHT",
            "aset": aset,
            "dag": dag,
            "ctrl": ctrl,
            "transform": transform,
            "name": name,
            "aset_id": _required_id(aset, "light animation set"),
            "dag_id": _required_id(dag, "light DAG"),
            "ctrl_id": _required_id(ctrl, "light transform control"),
            "transform_id": _required_id(transform, "light transform"),
            "locked": locked,
            "eligibility": eligibility["state"],
            "eligibility_reason": eligibility["reason_text"],
            "eligibility_help": eligibility["reason_help"],
            "eligibility_owner": eligibility["owner"],
            "reference_visits": eligibility["reference_visits"],
            "direct_child_count": eligibility["direct_child_count"],
        })

    rows.sort(key=lambda row: _natural_name_key(row["name"]))
    return rows


NATIVE_LIGHT_KIT_OWNER_NAME = u"lightkit"
NATIVE_LIGHT_KIT_MEMBER_NAMES = frozenset((
    u"keylight",
    u"filllight",
    u"rimlight",
    u"bouncelight",
))


def _resolve_plain_transform_owner(aset):
    try:
        if getattr(aset, "gameModel", None) is not None:
            return None
    except Exception:
        pass

    try:
        if getattr(aset, "camera", None) is not None:
            return None
    except Exception:
        pass

    if _resolve_projected_light(aset) is not None:
        return None

    try:
        root_group = aset.GetRootControlGroup()
    except Exception:
        return None

    if root_group is None:
        return None

    try:
        ctrl = root_group.FindControlByName("transform", True)
    except Exception:
        return None

    if ctrl is None:
        return None

    try:
        dag = ctrl.GetDag()
        transform = ctrl.GetTransform()
    except Exception:
        return None

    if dag is None or transform is None:
        return None

    try:
        transform_dag = transform.GetDag()
    except Exception:
        return None

    if transform_dag is None or not _same(transform_dag, dag):
        return None

    try:
        return {
            "aset": aset,
            "aset_id": _required_id(aset, "Light Kit animation set"),
            "dag": dag,
            "dag_id": _required_id(dag, "Light Kit root DAG"),
            "ctrl": ctrl,
            "ctrl_id": _required_id(ctrl, "Light Kit transform control"),
            "transform": transform,
            "transform_id": _required_id(transform, "Light Kit transform"),
        }
    except Exception:
        return None


def _animation_set_primary_dag(aset):
    pair = _resolve_projected_light(aset)

    if pair is not None:
        return pair[0]

    try:
        gm = getattr(aset, "gameModel", None)
    except Exception:
        gm = None

    if gm is not None:
        try:
            dag = movieobjects.CastElementAsDmeDag(gm)
        except Exception:
            dag = None

        if dag is not None:
            return dag

    try:
        camera = getattr(aset, "camera", None)
    except Exception:
        camera = None

    if camera is not None:
        try:
            dag = movieobjects.CastElementAsDmeDag(camera)
        except Exception:
            dag = None

        if dag is not None:
            return dag

    owner = _resolve_plain_transform_owner(aset)

    if owner is not None:
        return owner["dag"]

    return None


def _light_kit_external_scene_dependent(
    shot,
    root_id,
    member_dag_ids,
    owner_aset_id,
):
    allowed = frozenset(member_dag_ids)

    for aset in _shot_animation_sets_bounded(shot):
        try:
            aset_id = _required_id(aset, "scene animation set")
        except Exception:
            return {
                "complete": False,
                "dependent": None,
            }

        if aset_id == owner_aset_id:
            continue

        dag = _animation_set_primary_dag(aset)

        if dag is None:
            continue

        try:
            dag_id = _required_id(dag, "scene DAG")
        except Exception:
            return {
                "complete": False,
                "dependent": None,
            }

        if dag_id in allowed:
            continue

        parent_state = _optional_parent_state(dag)

        if not parent_state["complete"]:
            return {
                "complete": False,
                "dependent": None,
            }

        if parent_state["present"] and parent_state["id"] == root_id:
            return {
                "complete": True,
                "dependent": dag,
            }

    return {
        "complete": True,
        "dependent": None,
    }


def _native_light_kit_source(shot, light_rows, total_budget):
    owner_matches = []

    for aset in _shot_animation_sets_bounded(shot):
        try:
            name = _u(aset.GetName()).strip().lower()
        except Exception:
            continue

        if name != NATIVE_LIGHT_KIT_OWNER_NAME:
            continue

        owner = _resolve_plain_transform_owner(aset)

        if owner is not None:
            owner_matches.append(owner)

    if len(owner_matches) != 1:
        return None

    owner = owner_matches[0]
    root_id = owner["dag_id"]

    members = []

    for row in light_rows:
        try:
            parent = row["dag"].GetParent()
        except Exception:
            parent = None

        if parent is None:
            continue

        try:
            parent_id = _required_id(parent, "Light Kit light parent")
        except Exception:
            continue

        if parent_id == root_id:
            members.append(row)

    member_names = frozenset(
        _u(row["name"]).strip().lower() for row in members
    )

    if len(members) != 4 or member_names != NATIVE_LIGHT_KIT_MEMBER_NAMES:
        return None

    member_dag_ids = frozenset(
        row["dag_id"] for row in members
    )

    external_state = _light_kit_external_scene_dependent(
        shot,
        root_id,
        member_dag_ids,
        owner["aset_id"],
    )

    members_safe = all(
        row.get("eligibility") == "ELIGIBLE"
        for row in members
    )

    root_eligibility = _light_kit_root_eligibility(
        owner["dag"],
        total_budget
    )
    root_safe = (root_eligibility["state"] == "ELIGIBLE")

    external_safe = (
        external_state["complete"] and
        external_state["dependent"] is None
    )

    locked = not (members_safe and root_safe and external_safe)

    member_keys = tuple(sorted(
        (
            row["aset_id"],
            row["dag_id"],
            row["ctrl_id"],
            row["transform_id"],
        )
        for row in members
    ))

    if (
        external_state["complete"] and
        external_state["dependent"] is not None
    ):
        reason = LIGHT_KIT_EXTERNAL_TEXT
        owner_element = external_state["dependent"]
    else:
        reason = root_eligibility.get("reason_text") or LIGHT_KIT_UNKNOWN_TEXT
        owner_element = root_eligibility.get("owner")

    return {
        "kind": "LIGHT_KIT",
        "aset": owner["aset"],
        "dag": owner["dag"],
        "ctrl": owner["ctrl"],
        "transform": owner["transform"],
        "name": u"Light Kit",
        "aset_id": owner["aset_id"],
        "dag_id": owner["dag_id"],
        "ctrl_id": owner["ctrl_id"],
        "transform_id": owner["transform_id"],
        "members": members,
        "member_keys": member_keys,
        "locked": locked,
        "eligibility": "ELIGIBLE" if not locked else "UNKNOWN",
        "eligibility_reason": None if not locked else reason,
        "eligibility_help": None,
        "eligibility_owner": owner_element,
        "reference_visits": root_eligibility.get("reference_visits", 0),
        "direct_child_count": 0,
    }


def _inventory_sources(shot):
    total_budget = [0]
    light_rows = _inventory_lights(shot, total_budget)
    kit = _native_light_kit_source(shot, light_rows, total_budget)

    if kit is None:
        return light_rows

    hidden_ids = frozenset(
        row["dag_id"] for row in kit["members"]
    )

    rows = [
        row for row in light_rows
        if row["dag_id"] not in hidden_ids
    ]
    rows.append(kit)
    rows.sort(key=lambda row: _natural_name_key(row["name"]))
    return rows


# ---------------------------------------------------------------------------
# Model/body/face capabilities
# ---------------------------------------------------------------------------

def _root_frame(gm):
    origin = _vec3(gm.GetAbsPosition())
    q = gm.GetAbsOrientation()

    # _axes_from_quaternion returns local +X, +Y, +Z.
    # Source model right is local -Y, matching the anatomical body frame.
    _, forward, local_y, up = _axes_from_quaternion(q)
    right = _scale(local_y, -1.0)

    forward, right, up = _validate_orthogonal_axes(
        forward,
        right,
        up,
        "negative",
        "root frame"
    )

    return {
        "kind": "ROOT",
        "origin": origin,
        "forward": forward,
        "right": right,
        "up": up,
        "T": FALLBACK_NEARBY_SCALE,
    }


def _header_vector(hdr, name):
    """Read one known studiohdr_t Vector field."""
    try:
        value = getattr(hdr, name)
    except Exception:
        raise RuntimeError("studio header field unavailable: %s" % name)

    try:
        if callable(value):
            value = value()
    except Exception:
        pass

    return _vec3(value)


def _bounds_pair_valid(mins, maxs):
    mins = _require_finite_tuple(mins, "bounds mins")
    maxs = _require_finite_tuple(maxs, "bounds maxs")

    dims = (
        maxs[0] - mins[0],
        maxs[1] - mins[1],
        maxs[2] - mins[2],
    )

    if any(d < -EPS for d in dims):
        return False, None

    dims = tuple(max(0.0, d) for d in dims)
    max_dim = max(dims)

    if max_dim <= EPS or max_dim > MAX_PROP_BOUND_DIM:
        return False, None

    return True, dims


def _local_point_to_world(gm, point):
    point = _require_finite_tuple(point, "local point")

    origin = _vec3(gm.GetAbsPosition())
    _, local_x, local_y, local_z = _axes_from_quaternion(
        gm.GetAbsOrientation()
    )

    world = origin
    world = _add(world, _scale(local_x, point[0]))
    world = _add(world, _scale(local_y, point[1]))
    world = _add(world, _scale(local_z, point[2]))

    return _require_finite_tuple(world, "world point")


def _prop_bounds_frame(gm):
    """
    Generic model/prop placement frame.

    Source render-bounds convention:
        use view_bbmin/view_bbmax when either is non-zero;
        otherwise use hull_min/hull_max.

    Center/scale come from model bounds.
    Orientation comes from the evaluated gameModel root.
    """
    hdr = gm.GetStudioHdr()
    if hdr is None:
        raise RuntimeError("studio header unavailable")

    view_min = _header_vector(hdr, "view_bbmin")
    view_max = _header_vector(hdr, "view_bbmax")
    hull_min = _header_vector(hdr, "hull_min")
    hull_max = _header_vector(hdr, "hull_max")

    view_nonzero = any(
        abs(v) > EPS
        for v in (
            view_min[0], view_min[1], view_min[2],
            view_max[0], view_max[1], view_max[2],
        )
    )

    if view_nonzero:
        mins = view_min
        maxs = view_max
        source = "view_bb"
    else:
        mins = hull_min
        maxs = hull_max
        source = "hull"

    valid, dims = _bounds_pair_valid(mins, maxs)
    if not valid:
        raise RuntimeError("model bounds are not usable")

    local_center = (
        (mins[0] + maxs[0]) * 0.5,
        (mins[1] + maxs[1]) * 0.5,
        (mins[2] + maxs[2]) * 0.5,
    )

    world_center = _local_point_to_world(gm, local_center)

    _, forward, local_y, up = _axes_from_quaternion(
        gm.GetAbsOrientation()
    )
    right = _scale(local_y, -1.0)

    forward, right, up = _validate_orthogonal_axes(
        forward,
        right,
        up,
        "negative",
        "prop bounds frame"
    )

    sorted_dims = sorted(dims)
    median_dim = sorted_dims[1]
    max_dim = sorted_dims[2]
    min_dim = sorted_dims[0]

    T = median_dim * PROP_T_FROM_MEDIAN_DIM

    if not _finite_number(T) or T <= EPS:
        raise RuntimeError("prop placement scale invalid")

    root_origin = _vec3(gm.GetAbsPosition())

    illumination_local = None
    illumination_world = None
    try:
        illumination_local = _header_vector(hdr, "illumposition")
        illumination_world = _local_point_to_world(gm, illumination_local)
    except Exception:
        pass

    return {
        "kind": "BOUNDS",
        "origin": world_center,
        "torso_center": world_center,
        "forward": forward,
        "right": right,
        "up": up,
        "T": T,
        "bounds_source": source,
        "bounds_min": mins,
        "bounds_max": maxs,
        "bounds_dims": dims,
        "bounds_min_dim": min_dim,
        "bounds_median_dim": median_dim,
        "bounds_max_dim": max_dim,
        "bounds_aspect_max_to_median": (
            max_dim / median_dim if median_dim > EPS else 999999.0
        ),
        "bounds_local_center": local_center,
        "bounds_world_center": world_center,
        "root_origin": root_origin,
        "root_center_offset": _distance(root_origin, world_center),
        "illumination_local": illumination_local,
        "illumination_world": illumination_world,
    }


def _body_frame(gm):
    hdr = gm.GetStudioHdr()
    if hdr is None:
        raise RuntimeError("studio header unavailable")

    count = int(hdr.numbones)
    if count <= 0 or count > MAX_BONES:
        raise RuntimeError("bone count outside bounds")

    # Bone names in Workshop models are not reliably case-consistent.
    # Match the already-qualified family names case-insensitively, while
    # still requiring exactly one live bone for every landmark.
    by_lower = {}

    for i in range(count):
        actual_name = _u(hdr.pBone(i).pszName())
        key = actual_name.lower()
        by_lower.setdefault(key, []).append((actual_name, i))

    chosen = None

    for family, names in BODY_FAMILIES:
        keys = [n.lower() for n in names]

        if all(len(by_lower.get(key, [])) == 1 for key in keys):
            if chosen is not None:
                raise RuntimeError("ambiguous supported body family")
            chosen = (family, names, keys)

    if chosen is None:
        raise RuntimeError("no qualified body family")

    family, names, keys = chosen

    bones = gm.GetAttribute("bones")
    if bones is None:
        raise RuntimeError("live bones unavailable")

    live_count = len(bones)
    if live_count <= 0 or live_count > MAX_BONES:
        raise RuntimeError("live bone count outside bounds")

    pts = {}
    actual_names = []

    for canonical_name, key in zip(names, keys):
        actual_name, idx = by_lower[key][0]
        actual_names.append(actual_name)

        if idx >= live_count:
            raise RuntimeError("body landmark outside live bones")

        bone = movieobjects.CastElementAsDmeTransform(bones[idx])
        if bone is None:
            raise RuntimeError("body landmark cast failed")

        if int(gm.FindBone(bone)) != idx:
            raise RuntimeError("body landmark identity failed")

        dag = bone.GetDag()
        if dag is None or not _same(dag.GetTransform(), bone):
            raise RuntimeError("body landmark DAG identity failed")

        pts[canonical_name] = _vec3(dag.GetAbsPosition())

    lhip, rhip, lcollar, rcollar = [pts[n] for n in names]

    hip_right = _normalize(_sub(rhip, lhip))
    collar_right = _normalize(_sub(rcollar, lcollar))

    if _dot(hip_right, collar_right) < 0.0:
        raise RuntimeError("body side landmarks conflict")

    right = _normalize(_add(hip_right, collar_right))
    hip_mid = _mid(lhip, rhip)
    collar_mid = _mid(lcollar, rcollar)

    up_seed = _sub(collar_mid, hip_mid)
    up = _normalize(_sub(up_seed, _scale(right, _dot(up_seed, right))))

    forward = _normalize(_cross(up, right))
    up = _normalize(_cross(right, forward))

    forward, right, up = _validate_orthogonal_axes(
        forward,
        right,
        up,
        "negative",
        "body frame"
    )

    torso_center = _mid(hip_mid, collar_mid)
    T = _distance(hip_mid, collar_mid)

    if T <= EPS:
        raise RuntimeError("body scale degenerate")

    return {
        "kind": "BODY",
        "family": family,
        "actual_landmark_names": tuple(actual_names),
        "origin": torso_center,
        "torso_center": torso_center,
        "hip_mid": hip_mid,
        "collar_mid": collar_mid,
        "forward": forward,
        "right": right,
        "up": up,
        "T": T,
    }


def _copy_matrix(src):
    dst = vs.matrix3x4_t()

    for i in range(12):
        dst[i] = float(src[i])

    return dst


def _procedural_mask():
    mask = 0

    for name in (
        "BONE_PHYSICALLY_SIMULATED",
        "BONE_PHYSICS_PROCEDURAL",
        "BONE_ALWAYS_PROCEDURAL",
        "BONE_SCREEN_ALIGN_SPHERE",
        "BONE_SCREEN_ALIGN_CYLINDER",
    ):
        try:
            mask |= int(getattr(studio, name))
        except Exception:
            pass

    return mask


def _live_bone_position(gm, bones, idx):
    if idx < 0 or idx >= len(bones):
        raise RuntimeError("live bone index outside range")

    bone = movieobjects.CastElementAsDmeTransform(bones[idx])

    if bone is None or int(gm.FindBone(bone)) != idx:
        raise RuntimeError("live bone identity failed")

    dag = bone.GetDag()

    if dag is None or not _same(dag.GetTransform(), bone):
        raise RuntimeError("live bone DAG identity failed")

    return _vec3(dag.GetAbsPosition())


def _qualified_head_ancestor(hdr, start_idx, proc_mask):
    """
    For eye-bone fallback, allow the eye bone to reach a validated head bone
    either directly or through one non-head intermediate (e.g. FaceEyeSet_L).
    """
    bone_count = int(hdr.numbones)
    cur = start_idx
    seen = set()

    for depth in range(3):
        if cur < 0 or cur >= bone_count or cur in seen:
            raise RuntimeError("invalid eye-bone ancestry")

        seen.add(cur)
        hb = hdr.pBone(cur)

        if int(hb.proctype) != 0 or (int(hb.flags) & proc_mask) != 0:
            raise RuntimeError("procedural eye-bone ancestry not qualified")

        name = _u(hb.pszName())

        if name.lower() in tuple(n.lower() for n in VALIDATED_EYE_PARENT_BONES):
            return cur, name

        cur = int(hb.parent)

    raise RuntimeError("eye bones do not reach a qualified head bone")


def _face_frame_from_eye_bones(gm, hdr, body):
    if body is None or body.get("kind") != "BODY":
        raise RuntimeError("eye-bone fallback requires qualified body frame")

    bone_count = int(hdr.numbones)
    bones = gm.GetAttribute("bones")

    if bones is None:
        raise RuntimeError("live bones unavailable")

    if len(bones) <= 0 or len(bones) > MAX_BONES:
        raise RuntimeError("live bone count outside bounds")

    by_normalized = {}

    for i in range(bone_count):
        name = _u(hdr.pBone(i).pszName())
        key = re.sub(u"[^a-z0-9]+", u"", name.lower())
        by_normalized.setdefault(key, []).append((name, i))

    pair_families = (
        (u"eyeleft", u"eyeright"),
        (u"lefteye", u"righteye"),
    )

    candidates = []

    for left_key, right_key in pair_families:
        left = by_normalized.get(left_key, [])
        right = by_normalized.get(right_key, [])

        if len(left) == 1 and len(right) == 1:
            candidates.append((left[0], right[0]))

    if len(candidates) != 1:
        raise RuntimeError("exact left/right eye-bone pair is not unique")

    (left_name, left_idx), (right_name, right_idx) = candidates[0]

    proc_mask = _procedural_mask()

    left_head_idx, left_head_name = _qualified_head_ancestor(
        hdr,
        left_idx,
        proc_mask
    )
    right_head_idx, right_head_name = _qualified_head_ancestor(
        hdr,
        right_idx,
        proc_mask
    )

    if left_head_idx != right_head_idx:
        raise RuntimeError("left/right eye bones do not converge on one head")

    left_pos = _live_bone_position(gm, bones, left_idx)
    right_pos = _live_bone_position(gm, bones, right_idx)

    separation = _distance(left_pos, right_pos)
    ratio = separation / body["T"]

    if not _finite_number(ratio) or ratio < 0.02 or ratio > 0.35:
        raise RuntimeError("eye-bone separation outside qualified range")

    eye_right = _normalize(_sub(right_pos, left_pos))

    if _dot(eye_right, body["right"]) < 0.80:
        raise RuntimeError("eye-bone side direction conflicts with body frame")

    origin = _mid(left_pos, right_pos)

    # Keep orientation authority with the already-qualified body frame.
    # Eye-bone transforms can rotate independently for gaze/animation.
    forward = body["forward"]
    lateral = body["right"]
    up = body["up"]

    return {
        "origin": origin,
        "forward": forward,
        "lateral": lateral,
        "up": up,
        "parent_name": left_head_name,
        "source": "eye_bones",
        "left_eye_name": left_name,
        "right_eye_name": right_name,
        "eye_separation": separation,
    }


def _face_frame(gm, body=None):
    hdr = gm.GetStudioHdr()
    if hdr is None:
        raise RuntimeError("studio header unavailable")

    if int(hdr.numincludemodels) != 0:
        raise RuntimeError("included model not qualified")

    bone_count = int(hdr.numbones)
    if bone_count <= 0 or bone_count > MAX_BONES:
        raise RuntimeError("bone count outside bounds")

    num_att = int(hdr.GetNumAttachments())
    if num_att < 0 or num_att > MAX_ATTACHMENTS:
        raise RuntimeError("attachment count outside bounds")

    matches = []

    for i in range(num_att):
        att_name_raw = hdr.pAttachment(i).pszName()
        att_name_text = _u(att_name_raw)

        if att_name_text.lower() == "eyes":
            matches.append(
                (i, att_name_raw, att_name_text)
            )

    # Existing qualified attachment path remains authoritative.
    if len(matches) == 1:
        i, attachment_name_native, attachment_name = matches[0]
        att = hdr.pAttachment(i)

        # SFM's SWIG binding requires a narrow `char const *` here.
        # Use the exact raw spelling returned by studiohdr_t rather than
        # the decoded Python unicode display string.
        if int(gm.FindAttachment(attachment_name_native)) != i + 1:
            raise RuntimeError("eyes attachment lookup mismatch")

        flags = int(att.flags)

        if (flags & int(studio.ATTACHMENT_FLAG_WORLD_ALIGN)) != 0:
            raise RuntimeError("world-aligned eyes not qualified")

        localbone = int(att.localbone)
        mapped = int(hdr.GetAttachmentBone(i))

        if localbone != mapped:
            raise RuntimeError("eyes attachment remap mismatch")

        if mapped < 0 or mapped >= bone_count:
            raise RuntimeError("eyes attachment bone outside range")

        parent_name = _u(hdr.pBone(mapped).pszName())

        if parent_name.lower() not in tuple(
            n.lower() for n in VALIDATED_EYE_PARENT_BONES
        ):
            raise RuntimeError("eyes parent family not qualified")

        proc_mask = _procedural_mask()
        seen = set()
        cur = mapped

        for depth in range(MAX_PARENT_CHAIN):
            if cur < 0:
                break

            if cur >= bone_count or cur in seen:
                raise RuntimeError("invalid eyes ancestry")

            seen.add(cur)
            hb = hdr.pBone(cur)

            if int(hb.proctype) != 0 or (int(hb.flags) & proc_mask) != 0:
                raise RuntimeError("procedural eyes ancestry not qualified")

            cur = int(hb.parent)
        else:
            raise RuntimeError("eyes ancestry exceeds bound")

        bones = gm.GetAttribute("bones")

        if bones is None or mapped >= len(bones):
            raise RuntimeError("live eyes parent unavailable")

        bone = movieobjects.CastElementAsDmeTransform(bones[mapped])

        if bone is None or int(gm.FindBone(bone)) != mapped:
            raise RuntimeError("live eyes parent identity failed")

        dag = bone.GetDag()

        if dag is None or not _same(dag.GetTransform(), bone):
            raise RuntimeError("live eyes parent DAG identity failed")

        local_copy = _copy_matrix(att.local)
        world = vs.matrix3x4_t()

        vs.ConcatTransforms(dag.GetAbsTransform(), local_copy, world)

        vals = [float(world[j]) for j in range(12)]

        origin = _require_finite_tuple(
            (vals[3], vals[7], vals[11]),
            "eyes origin"
        )

        x_axis, y_axis, z_axis = _validate_orthogonal_axes(
            (vals[0], vals[4], vals[8]),
            (vals[1], vals[5], vals[9]),
            (vals[2], vals[6], vals[10]),
            "positive",
            "eyes frame"
        )

        native = _vec3(gm.ComputeAttachmentPosition(attachment_name_native))

        if _distance(origin, native) > VERIFY_POS_EPS:
            raise RuntimeError("eyes frame/native position disagreement")

        return {
            "origin": origin,
            "forward": x_axis,
            "lateral": y_axis,
            "up": z_axis,
            "parent_name": parent_name,
            "source": "attachment",
            "attachment_name": attachment_name,
        }

    # More than one exact `eyes` attachment is ambiguous and should not be
    # bypassed by another source. Zero attachments may use the strict bone pair.
    if len(matches) > 1:
        raise RuntimeError("exact eyes attachment is not unique")

    return _face_frame_from_eye_bones(
        gm,
        hdr,
        body
    )


# ---------------------------------------------------------------------------
# Conservative name-to-placement suggestions
# ---------------------------------------------------------------------------

def _split_name(name):
    s = _u(name)

    s = re.sub(u"([a-z0-9])([A-Z])", u"\\1 \\2", s)
    s = re.sub(u"([A-Za-z])([0-9]+)", u"\\1 \\2", s)
    s = re.sub(u"[^A-Za-z0-9]+", u" ", s)

    raw = [p.lower() for p in s.strip().split() if p]
    tokens = []

    for p in raw:
        p2 = re.sub(u"[0-9]+$", u"", p)

        if p2:
            tokens.append(p2)

    compact = u"".join(tokens)
    phrase = u" ".join(tokens)

    return tokens, compact, phrase


def _has_any(tokens, values):
    for value in values:
        if value in tokens:
            return True

    return False


def _suggest_role(name):
    tokens, compact, phrase = _split_name(name)
    hits = []

    dangerous_compacts = set((
        u"keyboard",
        u"monkey",
        u"donkey",
        u"eyebrow",
        u"eyebrows",
        u"sidekick",
    ))

    # Background before Backlight.
    if (
        _has_any(tokens, (u"background", u"bg", u"backdrop")) or
        compact in (u"background", u"backgroundlight", u"bglight", u"backdrop")
    ):
        hits.append(ROLE_BACKGROUND)

    eye_hit = (
        _has_any(tokens, (
            u"eye", u"eyes", u"eyelight",
            u"catch", u"catchlight", u"eyeglow"
        )) or
        compact in (
            u"eye", u"eyes", u"eyelight",
            u"catch", u"catchlight", u"eyeglow"
        ) or
        phrase in (u"eye light", u"catch light", u"eye glow")
    )

    if compact in dangerous_compacts:
        eye_hit = False

    if eye_hit:
        hits.append(ROLE_EYE)

    # Strong Floor Light aliases. These take precedence over generic Fill.
    floor_strong = (
        _has_any(tokens, (u"floor", u"floorfill", u"lowfill", u"uplight")) or
        phrase in (u"floor light", u"floor fill", u"low fill", u"up light") or
        compact == u"bouncelight"
    )

    if floor_strong:
        hits.append(ROLE_FLOOR)

    key_hit = (
        _has_any(tokens, (u"key", u"keylight")) or
        phrase == u"key light" or
        compact == u"keylight"
    )

    if compact in dangerous_compacts:
        key_hit = False

    if key_hit:
        hits.append(ROLE_KEY)

    if (
        not floor_strong and
        (
            _has_any(tokens, (u"fill", u"filllight")) or
            phrase == u"fill light" or
            compact == u"filllight"
        )
    ):
        hits.append(ROLE_FILL)

    if (
        _has_any(tokens, (u"hair", u"hairlight")) or
        phrase == u"hair light" or
        compact == u"hairlight"
    ):
        hits.append(ROLE_HAIR)

    if (
        _has_any(tokens, (
            u"rim", u"rimlight",
            u"edge", u"edgelight",
            u"separation", u"sep"
        )) or
        phrase in (u"rim light", u"edge light") or
        compact in (u"rimlight", u"edgelight")
    ):
        hits.append(ROLE_RIM)

    if ROLE_BACKGROUND not in hits:
        if (
            _has_any(tokens, (u"back", u"backlight")) or
            phrase == u"back light" or
            compact == u"backlight"
        ):
            hits.append(ROLE_BACK)

    ambiguous = _has_any(tokens, (
        u"accent",
        u"practical",
        u"bounce",
        u"kicker",
        u"kick",
    ))

    # Exact bounceLight is the qualified SFM Floor Light alias.
    # Generic Bounce remains intentionally ambiguous.
    if compact == u"bouncelight":
        ambiguous = False

    unique = []

    for hit in hits:
        if hit not in unique:
            unique.append(hit)

    if ambiguous:
        return ROLE_NEARBY, unique, True

    if len(unique) == 1:
        return unique[0], unique, False

    return ROLE_NEARBY, unique, (len(unique) > 1)


# ---------------------------------------------------------------------------
# Chooser
# ---------------------------------------------------------------------------

def _apply_dialog_font(dialog, point_delta=3):
    """Apply a visibly larger font directly to dialog child widgets.

    SFM's Qt styling can override/inhibit simple parent-font inheritance, so
    this resolves the application font and assigns the enlarged font directly
    to the widgets after the dialog has been constructed.
    """
    try:
        font = QtGui.QApplication.font()
        point_size = int(font.pointSize())

        if point_size > 0:
            font.setPointSize(point_size + int(point_delta))
        else:
            pixel_size = int(font.pixelSize())

            if pixel_size <= 0:
                try:
                    pixel_size = int(QtGui.QFontInfo(font).pixelSize())
                except Exception:
                    pixel_size = -1

            if pixel_size > 0:
                # Roughly equivalent to +3 pt at common desktop DPI.
                font.setPixelSize(pixel_size + 4)
            else:
                return

        dialog.setFont(font)

        for widget in dialog.findChildren(QtGui.QWidget):
            try:
                widget.setFont(font)
            except Exception:
                pass
    except Exception:
        pass


class BringNearHelpDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Bring Near: Lights - Help")
        _apply_window_icon(self)
        self.setModal(True)

        try:
            self.setWindowFlags(
                self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
            )
        except Exception:
            pass

        self.resize(780, 500)

        outer = QtGui.QVBoxLayout(self)

        intro1 = QtGui.QLabel(HELP_INTRO_1)
        intro1.setWordWrap(True)
        outer.addWidget(intro1)

        table = QtGui.QTableWidget(len(HELP_TABLE), 3)
        table.setHorizontalHeaderLabels((
            "Placement",
            "Starting position",
            "Points toward",
        ))
        table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

        for row_index, row in enumerate(HELP_TABLE):
            for col_index, value in enumerate(row):
                item = QtGui.QTableWidgetItem(value)
                table.setItem(row_index, col_index, item)

        try:
            header = table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setHighlightSections(False)
        except Exception:
            pass

        # Apply the same enlarged font before measuring the Help table so its
        # geometry is calculated from the font the user actually sees.
        _apply_dialog_font(self, 3)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        # Give the Help rows a little more breathing room without making the
        # table feel loose.
        for i in range(table.rowCount()):
            table.setRowHeight(i, table.rowHeight(i) + 5)

        table.setColumnWidth(0, max(table.columnWidth(0), 120))
        table.setColumnWidth(1, max(table.columnWidth(1), 340))

        # Fit the table to the full enlarged row content and suppress the
        # useless tiny vertical scrollbar.
        try:
            table_height = table.horizontalHeader().height()
            table_height += table.verticalHeader().length()
            table_height += (2 * table.frameWidth()) + 6
            table.setFixedHeight(table_height)
            table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        except Exception:
            pass

        outer.addWidget(table)

        duplicates = QtGui.QLabel(HELP_DUPLICATES)
        duplicates.setWordWrap(True)
        outer.addWidget(duplicates)

        bottom = QtGui.QLabel(HELP_BOTTOM)
        bottom.setWordWrap(True)
        outer.addWidget(bottom)

        footer = QtGui.QHBoxLayout()

        license_label = QtGui.QLabel(HELP_LICENSE)
        license_label.setTextFormat(QtCore.Qt.PlainText)
        footer.addWidget(license_label)
        footer.addStretch(1)

        buttons = QtGui.QDialogButtonBox()
        close_button = buttons.addButton(
            "Close",
            QtGui.QDialogButtonBox.AcceptRole
        )
        close_button.clicked.connect(self.accept)
        footer.addWidget(buttons)

        outer.addLayout(footer)

        _apply_dialog_font(self, 3)


class BringNearDialog(QtGui.QDialog):
    def __init__(
        self,
        rows,
        placement_available,
        eye_available,
        eye_note_needed,
        model_name,
        light_kit_available,
        parent=None,
    ):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle(UI_TITLE)
        _apply_window_icon(self)
        self.setModal(True)

        # The default Qt dialog flag exposes a title-bar "?" button that enters
        # What's This? cursor mode. PC1 does not use that interaction model.
        # Remove it and provide an explicit Help button instead.
        try:
            self.setWindowFlags(
                self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
            )
        except Exception:
            pass

        self.resize(575, 560)

        self._rows = []
        self._continued = False
        self._model_name = _u(model_name)
        self._body_available = bool(placement_available)
        self._eye_available = bool(eye_available)
        self._light_kit_available = bool(light_kit_available)

        outer = QtGui.QVBoxLayout(self)

        top = QtGui.QLabel(UI_TOP)
        top.setWordWrap(True)
        outer.addWidget(top)

        if not self._body_available:
            note = QtGui.QLabel(BODY_HELP)
            note.setWordWrap(True)
            outer.addWidget(note)

        if self._body_available and eye_note_needed and not self._eye_available:
            note = QtGui.QLabel(EYE_HELP)
            note.setWordWrap(True)
            outer.addWidget(note)

        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtGui.QFrame.NoFrame)

        body = QtGui.QWidget()
        grid = QtGui.QGridLayout(body)
        grid.setContentsMargins(4, 2, 4, 2)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(5)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)
        grid.setAlignment(QtCore.Qt.AlignTop)

        grid.addWidget(QtGui.QLabel("<b>Move</b>"), 0, 0)
        grid.addWidget(QtGui.QLabel("<b>Light name</b>"), 0, 1)
        grid.addWidget(QtGui.QLabel("<b>Placement</b>"), 0, 2)

        def _add_row_band(row_index):
            if (row_index % 2) != 1:
                return

            band = QtGui.QFrame()
            band.setFrameShape(QtGui.QFrame.NoFrame)
            band.setStyleSheet(
                "QFrame { background-color: #393939; }"
            )
            band.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

            # Span the complete row. Add it before the row controls and lower it
            # so native checkboxes, labels, and combo boxes remain fully intact.
            grid.addWidget(band, row_index, 0, 1, 3)
            band.lower()

        row_no = 1

        for source in rows:
            name_label = QtGui.QLabel(source["name"])
            name_label.setTextFormat(QtCore.Qt.PlainText)
            name_label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

            is_light_kit = (source.get("kind") == "LIGHT_KIT")

            if is_light_kit and not self._light_kit_available:
                blank = QtGui.QLabel("")
                unavailable = QtGui.QLabel(LIGHT_KIT_BODY_TEXT)
                unavailable.setWordWrap(True)

                _add_row_band(row_no)

                grid.addWidget(blank, row_no, 0)
                grid.addWidget(name_label, row_no, 1)
                grid.addWidget(unavailable, row_no, 2)

                self._rows.append({
                    "source": source,
                    "checkbox": None,
                    "combo": None,
                })

                row_no += 1
                continue

            if source["locked"]:
                blank = QtGui.QLabel("")
                locked = QtGui.QLabel(source["eligibility_reason"])
                locked.setWordWrap(True)

                if not is_light_kit:
                    locked.setToolTip(source["eligibility_help"])
                    name_label.setToolTip(source["eligibility_help"])

                _add_row_band(row_no)

                grid.addWidget(blank, row_no, 0)
                grid.addWidget(name_label, row_no, 1)
                grid.addWidget(locked, row_no, 2)

                self._rows.append({
                    "source": source,
                    "checkbox": None,
                    "combo": None,
                })

                row_no += 1
                continue

            cb = QtGui.QCheckBox()

            if is_light_kit:
                placement_label = QtGui.QLabel(LIGHT_KIT_PLACEMENT_TEXT)
                placement_label.setMinimumWidth(250)
                placement_label.setMaximumWidth(250)

                _add_row_band(row_no)

                grid.addWidget(cb, row_no, 0)
                grid.addWidget(name_label, row_no, 1)
                grid.addWidget(placement_label, row_no, 2)

                self._rows.append({
                    "source": source,
                    "checkbox": cb,
                    "combo": None,
                })

                row_no += 1
                continue

            combo = QtGui.QComboBox()
            combo.setMinimumWidth(250)
            combo.setMaximumWidth(250)

            for role in ROLE_ORDER:
                combo.addItem(role)

            model = combo.model()

            for i in range(combo.count()):
                role = _u(combo.itemText(i))
                enabled = True
                help_text = ROLE_DESCRIPTIONS.get(role, "")

                if role in BODY_ROLES and not self._body_available:
                    enabled = False
                    help_text = BODY_HELP

                if role == ROLE_EYE and not self._eye_available:
                    enabled = False
                    help_text = EYE_HELP

                try:
                    item = model.item(i)

                    if item is not None:
                        item.setEnabled(enabled)
                        item.setToolTip(help_text)
                except Exception:
                    pass

            suggestion = source["suggestion"]

            if suggestion in BODY_ROLES and not self._body_available:
                suggestion = ROLE_NEARBY

            if suggestion == ROLE_EYE and not self._eye_available:
                suggestion = ROLE_NEARBY
                name_label.setToolTip(EYE_HELP)

            idx = combo.findText(suggestion)

            if idx >= 0:
                combo.setCurrentIndex(idx)

            _add_row_band(row_no)

            grid.addWidget(cb, row_no, 0)
            grid.addWidget(name_label, row_no, 1)
            grid.addWidget(combo, row_no, 2)

            self._rows.append({
                "source": source,
                "checkbox": cb,
                "combo": combo,
            })


            row_no += 1

        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        divider = QtGui.QFrame()
        divider.setFrameShape(QtGui.QFrame.HLine)
        divider.setFrameShadow(QtGui.QFrame.Sunken)
        outer.addWidget(divider)

        selection_row = QtGui.QHBoxLayout()
        select_all_button = QtGui.QPushButton("Select All")
        clear_all_button = QtGui.QPushButton("Clear All")
        self._flip_sides = QtGui.QCheckBox(
            "Flip Key / Fill / Rim sides"
        )
        self._flip_sides.setToolTip(
            "Moves Key, Fill, and Rim to the opposite sides."
        )

        selection_row.addWidget(select_all_button)
        selection_row.addWidget(clear_all_button)
        selection_row.addStretch(1)
        selection_row.addWidget(self._flip_sides)

        select_all_button.clicked.connect(self._select_all)
        clear_all_button.clicked.connect(self._clear_all)

        outer.addLayout(selection_row)

        button_row = QtGui.QHBoxLayout()

        model_label = QtGui.QLabel(
            u"Model: %s" % self._model_name
        )
        model_label.setTextFormat(QtCore.Qt.PlainText)

        self._bring = QtGui.QPushButton("Bring Near")
        self._bring.setMinimumWidth(92)
        self._bring.setStyleSheet(
            "QPushButton {"
            " background-color: #2f6fa6;"
            " color: white;"
            " border: 1px solid #4a82b2;"
            " border-radius: 2px;"
            " padding: 4px 12px;"
            " font-weight: bold;"
            "}"
            "QPushButton:hover {"
            " background-color: #377fba;"
            "}"
            "QPushButton:pressed {"
            " background-color: #275d8b;"
            "}"
            "QPushButton:disabled {"
            " background-color: #3b3b3b;"
            " color: #777777;"
            " border-color: #4a4a4a;"
            "}"
        )
        help_button = QtGui.QPushButton("Help")
        close_button = QtGui.QPushButton("Close")

        button_row.addWidget(model_label)
        button_row.addStretch(1)
        button_row.addWidget(self._bring)
        button_row.addWidget(help_button)
        button_row.addWidget(close_button)

        self._bring.clicked.connect(self._continue)
        help_button.clicked.connect(self._show_help)
        close_button.clicked.connect(self.reject)

        for info in self._rows:
            cb = info["checkbox"]
            if cb is not None:
                cb.toggled.connect(self._update_bring_enabled)

        self._update_bring_enabled()
        outer.addLayout(button_row)

        _apply_dialog_font(self, 3)

    def _update_bring_enabled(self, checked=None):
        has_selection = False

        for info in self._rows:
            cb = info["checkbox"]

            if cb is not None and cb.isChecked():
                has_selection = True
                break

        self._bring.setEnabled(has_selection)

    def _select_all(self):
        for info in self._rows:
            cb = info["checkbox"]

            if cb is not None:
                cb.setChecked(True)

    def _clear_all(self):
        for info in self._rows:
            cb = info["checkbox"]

            if cb is not None:
                cb.setChecked(False)

    def _show_help(self):
        try:
            dlg = BringNearHelpDialog(self)
            dlg.exec_()
        except Exception:
            pass

    def _continue(self):
        has_selection = False

        for info in self._rows:
            cb = info["checkbox"]

            if cb is not None and cb.isChecked():
                has_selection = True
                break

        if not has_selection:
            _show_info(MSG_SELECT_LIGHT)
            return

        self._continued = True
        self.accept()

    def continued(self):
        return self._continued

    def flip_sides(self):
        return bool(self._flip_sides.isChecked())

    def selections(self):
        result = []

        for info in self._rows:
            cb = info["checkbox"]
            combo = info["combo"]

            if cb is None:
                continue

            if not cb.isChecked():
                continue

            source = info["source"]

            if source.get("kind") == "LIGHT_KIT":
                result.append({
                    "source": source,
                    "role": ROLE_LIGHT_KIT,
                })
                continue

            if combo is None:
                continue

            result.append({
                "source": source,
                "role": _u(combo.currentText()),
            })

        return result


# ---------------------------------------------------------------------------
# Placement planning
# ---------------------------------------------------------------------------

def _duplicate_offset(index):
    if index <= 0:
        return 0.0

    n = (index + 1) // 2
    sign = 1.0 if (index % 2) == 1 else -1.0

    return sign * 0.25 * float(n)


def _selected_groups(selections):
    groups = {}

    for sel in selections:
        role = sel["role"]
        groups.setdefault(role, []).append(sel)

    for role in groups:
        groups[role].sort(
            key=lambda s: (
                _u(s["source"]["name"]).lower(),
                _u(s["source"]["dag_id"] or u"")
            )
        )

    return groups


def _placement_target(role, frame):
    T = frame["T"]
    up = frame["up"]
    origin = frame["origin"]

    if frame.get("kind") == "BODY":
        collar = frame["collar_mid"]
        torso = frame["torso_center"]

        if role in (ROLE_KEY, ROLE_FILL):
            return _add(collar, _scale(up, 0.10 * T))

        if role in (ROLE_BACK, ROLE_RIM):
            return _add(collar, _scale(up, -0.10 * T))

        if role == ROLE_HAIR:
            return _add(collar, _scale(up, 0.70 * T))

        if role == ROLE_FLOOR:
            return _add(torso, _scale(up, 0.30 * T))

        if role == ROLE_BACKGROUND:
            target = torso
            target = _add(target, _scale(frame["forward"], -2.75 * T))
            target = _add(target, _scale(up, 0.25 * T))
            return target

    # Generic bounds fallback: ordinary role lights aim at the bounds center.
    # Background remains a set-facing placement and aims behind the object.
    if role == ROLE_BACKGROUND:
        target = origin
        target = _add(target, _scale(frame["forward"], -2.75 * T))
        target = _add(target, _scale(up, 0.25 * T))
        return target

    if role in BODY_ROLES:
        return origin

    raise RuntimeError("unsupported placement target role")


def _placement_role_plan(role, dup_index, frame, flip_sides=False):
    T = frame["T"]
    fwd = frame["forward"]
    right = frame["right"]
    up = frame["up"]
    origin = frame["origin"]

    off_f, off_r, off_u = BODY_ROLE_OFFSETS[role]

    if flip_sides and role in (ROLE_KEY, ROLE_FILL, ROLE_RIM):
        off_r = -off_r

    off_u += _duplicate_offset(dup_index)

    dest = origin
    dest = _add(dest, _scale(fwd, off_f * T))
    dest = _add(dest, _scale(right, off_r * T))
    dest = _add(dest, _scale(up, off_u * T))

    target = _placement_target(role, frame)
    q = _aim_quaternion(dest, target, up)

    return {
        "dest": dest,
        "q": q,
        "rotate_xyz": _rotate_xyz_for_quaternion(q),
        "keep_direction": False,
        "target": target,
    }



def _eye_role_plan(dup_index, dup_count, placement, face):
    dest = _add(
        face["origin"],
        _scale(face["forward"], EYE_DISTANCE)
    )

    # Multiple Eye Lights form a centered row in front of the eyes.
    # Neighboring lights are separated by 0.35 T.
    if dup_count > 1:
        T = placement["T"] if placement is not None else FALLBACK_NEARBY_SCALE
        center_index = (float(dup_count) - 1.0) * 0.5
        lateral = (float(dup_index) - center_index) * 0.35 * T

        dest = _add(
            dest,
            _scale(face["lateral"], lateral)
        )

    q = _aim_quaternion(
        dest,
        face["origin"],
        face["up"]
    )

    return {
        "dest": dest,
        "q": q,
        "rotate_xyz": _rotate_xyz_for_quaternion(q),
        "keep_direction": False,
        "target": face["origin"],
    }


def _nearby_role_plan(nearby_index, placement, root, current_q):
    frame = placement if placement is not None else root

    if frame is None:
        raise RuntimeError("Nearby Only has no usable placement frame")

    T = frame["T"]

    columns = (0.0, 0.45, -0.45)
    col = nearby_index % 3
    row = nearby_index // 3

    dest = frame["origin"]
    dest = _add(dest, _scale(frame["right"], -2.60 * T))
    dest = _add(dest, _scale(frame["forward"], columns[col] * T))
    dest = _add(dest, _scale(frame["up"], (0.75 + 0.45 * row) * T))

    return {
        "dest": dest,
        "q": current_q,
        "rotate_xyz": _rotate_xyz_for_quaternion(current_q),
        "keep_direction": True,
        "target": None,
    }


def _build_plans(selections, placement, face, root, flip_sides=False):
    groups = _selected_groups(selections)
    plans = []
    nearby_counter = 0

    for role in ROLE_ORDER:
        group = groups.get(role, [])

        for dup_index, sel in enumerate(group):
            source = sel["source"]
            dag = source["dag"]
            current_q = dag.GetAbsOrientation()

            if role in BODY_ROLES:
                if placement is None:
                    raise RuntimeError("placement role without placement capability")

                plan = _placement_role_plan(
                    role,
                    dup_index,
                    placement,
                    flip_sides=flip_sides
                )

            elif role == ROLE_EYE:
                if face is None:
                    raise RuntimeError("eye role without eye capability")

                plan = _eye_role_plan(
                    dup_index,
                    len(group),
                    placement,
                    face
                )

            elif role == ROLE_NEARBY:
                plan = _nearby_role_plan(
                    nearby_counter,
                    placement,
                    root,
                    current_q
                )
                nearby_counter += 1

            else:
                raise RuntimeError("unknown role")

            plan["selection"] = sel
            plan["role"] = role
            plans.append(plan)

    for sel in selections:
        if sel["role"] != ROLE_LIGHT_KIT:
            continue

        if placement is None or placement.get("kind") != "BODY":
            raise RuntimeError(
                "Light Kit selected without BODY placement capability"
            )

        source = sel["source"]
        dag = source["dag"]
        current_q = dag.GetAbsOrientation()

        plans.append({
            "dest": placement["torso_center"],
            "q": current_q,
            "rotate_xyz": _rotate_xyz_for_quaternion(current_q),
            "keep_direction": True,
            "target": None,
            "selection": sel,
            "role": ROLE_LIGHT_KIT,
            "light_kit": True,
        })

    return plans


# ---------------------------------------------------------------------------
# Re-resolution and selected-source safety
# ---------------------------------------------------------------------------

def _re_resolve(shot, selections):
    current = _inventory_sources(shot)
    by_dag_id = {}

    for item in current:
        dag_id = item.get("dag_id")

        if dag_id is None:
            raise RuntimeError("current light identity unavailable")

        by_dag_id.setdefault(dag_id, []).append(item)

    rebound = []

    for sel in selections:
        original = sel["source"]

        required_keys = (
            "aset_id",
            "dag_id",
            "ctrl_id",
            "transform_id",
        )

        for key in required_keys:
            if original.get(key) is None:
                raise RuntimeError("selected light identity incomplete")

        matches = by_dag_id.get(original["dag_id"], [])

        if len(matches) == 0:
            raise RuntimeError("selected light disappeared")

        if len(matches) != 1:
            raise RuntimeError("selected light identity became ambiguous")

        item = matches[0]

        if original.get("kind", "LIGHT") != item.get("kind", "LIGHT"):
            raise RuntimeError("selected source kind changed")

        for key, label in (
            ("aset_id", "animation-set"),
            ("dag_id", "DAG"),
            ("ctrl_id", "transform-control"),
            ("transform_id", "transform"),
        ):
            if item.get(key) is None:
                raise RuntimeError("%s identity became unavailable" % label)

            if original[key] != item[key]:
                raise RuntimeError("%s identity changed" % label)

        if item.get("kind") == "LIGHT_KIT":
            if original.get("member_keys") != item.get("member_keys"):
                raise RuntimeError("Light Kit membership changed")

        rebound.append({
            "source": item,
            "role": sel["role"],
        })

    return rebound


def _locked_selected(selections):
    for sel in selections:
        item = sel["source"]

        if item.get("eligibility") != "ELIGIBLE":
            return True

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    write_attempted = False
    pushed = False
    record_mode = False

    try:
        anchor = sfm.GetCurrentAnimationSet()
        shot = sfm.GetCurrentShot()
        live_shot = sfmApp.GetShotAtCurrentTime()

        timeline_before = _timeline_snapshot()

        if anchor is None or shot is None or live_shot is None:
            _show_warning(MSG_OPEN_FAIL)
            return

        if not _same(shot, live_shot):
            _show_warning(MSG_CONTEXT_FAIL)
            return

        anchor_id = _required_id(anchor, "anchor animation set")
        shot_id = _required_id(shot, "script shot")

        try:
            gm = anchor.gameModel
        except Exception:
            gm = None

        if gm is None:
            _show_warning("Run Bring Near from a model or prop.")
            return

        gm_id = _required_id(gm, "anchor gameModel")

        body = None

        try:
            body = _body_frame(gm)
        except Exception:
            body = None

        bounds = None

        if body is None:
            try:
                bounds = _prop_bounds_frame(gm)
            except Exception:
                bounds = None

        placement = body if body is not None else bounds
        root = None

        if placement is None:
            try:
                root = _root_frame(gm)
            except Exception:
                root = None
                _show_warning(MSG_OPEN_FAIL)
                return

        face = None

        try:
            face = _face_frame(gm, body)
        except Exception:
            face = None

        lights = _inventory_sources(shot)

        if not lights:
            _show_info(MSG_NO_LIGHTS)
            return

        eye_note_needed = False

        for item in lights:
            if item.get("kind") == "LIGHT_KIT":
                item["suggestion"] = ROLE_LIGHT_KIT
                continue

            suggestion, hits, ambiguous = _suggest_role(item["name"])

            if suggestion == ROLE_EYE:
                eye_note_needed = True

            effective = suggestion

            if effective in BODY_ROLES and placement is None:
                effective = ROLE_NEARBY

            if effective == ROLE_EYE and face is None:
                effective = ROLE_NEARBY

            item["suggestion"] = effective

        try:
            model_display_name = _u(anchor.GetName())
        except Exception:
            model_display_name = u"Model"

        dlg = BringNearDialog(
            lights,
            placement_available=(placement is not None),
            eye_available=(face is not None),
            eye_note_needed=eye_note_needed,
            model_name=model_display_name,
            light_kit_available=(
                body is not None and body.get("kind") == "BODY"
            ),
            parent=_active_window(),
        )

        dlg.exec_()

        if not dlg.continued():
            return

        selected = dlg.selections()

        if not selected:
            return

        if placement is None:
            invalid_placement_roles = [
                sel["role"] for sel in selected if sel["role"] in BODY_ROLES
            ]

            if invalid_placement_roles:
                raise RuntimeError(
                    "placement role selected while placement frame unavailable"
                )

        if face is None:
            eye_selected = any(sel["role"] == ROLE_EYE for sel in selected)

            if eye_selected:
                raise RuntimeError(
                    "Eye Light selected while eye capability unavailable"
                )

        kit_selected = any(
            sel["role"] == ROLE_LIGHT_KIT for sel in selected
        )

        if kit_selected and (body is None or body.get("kind") != "BODY"):
            raise RuntimeError(
                "Light Kit selected while BODY capability unavailable"
            )

        timeline_after = _timeline_snapshot()
        context_ok, context_reason = _same_timeline_context(
            timeline_before,
            timeline_after
        )

        if not context_ok:
            _show_warning(MSG_CONTEXT_FAIL)
            return

        anchor_after = sfm.GetCurrentAnimationSet()

        if (
            anchor_after is None or
            _required_id(anchor_after, "post-dialog anchor") != anchor_id
        ):
            _show_warning(MSG_CONTEXT_FAIL)
            return

        try:
            gm_after = anchor_after.gameModel
        except Exception:
            gm_after = None

        if (
            gm_after is None or
            _required_id(gm_after, "post-dialog gameModel") != gm_id
        ):
            _show_warning(MSG_CONTEXT_FAIL)
            return

        if _required_id(shot, "script shot") != shot_id:
            _show_warning(MSG_CONTEXT_FAIL)
            return

        gm = gm_after
        selected = _re_resolve(shot, selected)

        if _locked_selected(selected):
            _show_warning(MSG_LOCK_FAIL)
            return

        body2 = None
        bounds2 = None
        root2 = None

        if body is not None:
            try:
                body2 = _body_frame(gm)
            except Exception:
                _show_warning(MSG_CONTEXT_FAIL)
                return
        elif bounds is not None:
            try:
                bounds2 = _prop_bounds_frame(gm)
            except Exception:
                _show_warning(MSG_CONTEXT_FAIL)
                return

        placement2 = body2 if body2 is not None else bounds2

        if placement2 is None:
            try:
                root2 = _root_frame(gm)
            except Exception:
                _show_warning(MSG_CONTEXT_FAIL)
                return

        face2 = None
        need_eye = any(sel["role"] == ROLE_EYE for sel in selected)

        if need_eye:
            try:
                face2 = _face_frame(gm, body2)
            except Exception:
                _show_warning(EYE_HELP)
                return
        elif face is not None:
            try:
                face2 = _face_frame(gm, body2)
            except Exception:
                face2 = None

        # Freeze the whole selected batch before any write.
        plans = _build_plans(
            selected,
            placement2,
            face2,
            root2,
            flip_sides=dlg.flip_sides()
        )

        for plan in plans:
            dag = plan["selection"]["source"]["dag"]

            plan["before_pos"] = _vec3(dag.GetAbsPosition())
            plan["before_q"] = _quat4(dag.GetAbsOrientation())
            plan["before_parent_state"] = _optional_parent_state(dag)

            if not plan["before_parent_state"]["complete"]:
                raise RuntimeError("source parent could not be verified")

            plan["dest"] = _require_finite_tuple(
                plan["dest"],
                "planned destination"
            )
            plan["rotate_xyz"] = _require_finite_tuple(
                plan["rotate_xyz"],
                "planned rotation"
            )
            plan["target_q4"] = _quat4(plan["q"])

            if plan.get("light_kit"):
                members_before = {}

                for member in plan["selection"]["source"]["members"]:
                    member_dag = member["dag"]
                    member_parent = _optional_parent_state(member_dag)

                    if not member_parent["complete"]:
                        raise RuntimeError(
                            "Light Kit member parent could not be verified"
                        )

                    members_before[member["dag_id"]] = {
                        "pos": _vec3(member_dag.GetAbsPosition()),
                        "q": _quat4(member_dag.GetAbsOrientation()),
                        "parent_state": member_parent,
                    }

                plan["members_before"] = members_before

        to_write = []

        for plan in plans:
            pos_err = _distance(
                plan["before_pos"],
                plan["dest"]
            )

            if plan["keep_direction"]:
                noop = (pos_err <= NOOP_POS_EPS)
            else:
                ori_err = _qangle_deg(
                    plan["before_q"],
                    plan["target_q4"]
                )

                noop = (
                    pos_err <= NOOP_POS_EPS and
                    ori_err <= NOOP_ANG_DEG
                )

            if not noop:
                to_write.append(plan)

        if not to_write:
            _show_info(MSG_NOOP)
            return

        sfm.PushSelection()
        pushed = True

        sfm.ClearSelection()
        sfm.SetOperationMode("Record")
        record_mode = True

        for plan in to_write:
            source = plan["selection"]["source"]
            dag = source["dag"]

            sfm.ClearSelection()
            sfm.SelectDag(dag)

            if not _same(sfm.FirstSelectedDag(), dag):
                raise RuntimeError("target selection mismatch")

            write_attempted = True

            d = plan["dest"]

            sfm.Move(
                d[0],
                d[1],
                d[2],
                relative=False,
                offsetMode=False,
                space="World",
            )

            if not plan.get("light_kit"):
                r = plan["rotate_xyz"]

                sfm.Rotate(
                    r[0],
                    r[1],
                    r[2],
                    relative=False,
                    offsetMode=False,
                    space="World",
                )

            after_pos = _vec3(dag.GetAbsPosition())
            after_q = dag.GetAbsOrientation()

            pos_err = _distance(
                after_pos,
                d
            )

            if not _finite_number(pos_err):
                raise RuntimeError("position verification was non-finite")

            if plan["keep_direction"]:
                ori_err = _qangle_deg(
                    _quat4(after_q),
                    plan["before_q"]
                )
            else:
                ori_err = _qangle_deg(
                    _quat4(after_q),
                    plan["target_q4"]
                )

            after_parent_state = _optional_parent_state(dag)
            parent_ok = _same_optional_parent(
                plan["before_parent_state"],
                after_parent_state
            )

            if not _finite_number(ori_err):
                raise RuntimeError("orientation verification was non-finite")

            if pos_err > VERIFY_POS_EPS:
                raise RuntimeError("destination verification failed")

            if ori_err > NOOP_ANG_DEG:
                raise RuntimeError("orientation verification failed")

            if not parent_ok:
                raise RuntimeError("parent verification failed")

            if plan.get("light_kit"):
                expected_delta = _sub(
                    plan["dest"],
                    plan["before_pos"]
                )

                current_members = {
                    member["dag_id"]: member
                    for member in source["members"]
                }
                before_members = plan["members_before"]

                if set(current_members.keys()) != set(before_members.keys()):
                    raise RuntimeError(
                        "Light Kit member set changed during move"
                    )

                for member_id, before_member in before_members.items():
                    member = current_members[member_id]
                    member_dag = member["dag"]

                    member_after_pos = _vec3(
                        member_dag.GetAbsPosition()
                    )
                    member_after_q = _quat4(
                        member_dag.GetAbsOrientation()
                    )
                    member_after_parent = _optional_parent_state(
                        member_dag
                    )

                    actual_delta = _sub(
                        member_after_pos,
                        before_member["pos"]
                    )

                    if _distance(
                        actual_delta,
                        expected_delta
                    ) > VERIFY_POS_EPS:
                        raise RuntimeError(
                            "Light Kit member translation verification failed"
                        )

                    if _qangle_deg(
                        member_after_q,
                        before_member["q"]
                    ) > NOOP_ANG_DEG:
                        raise RuntimeError(
                            "Light Kit member orientation verification failed"
                        )

                    if not _same_optional_parent(
                        before_member["parent_state"],
                        member_after_parent
                    ):
                        raise RuntimeError(
                            "Light Kit member parent verification failed"
                        )

    except Exception:
        if write_attempted:
            _show_warning(MSG_PARTIAL)
        elif 'dlg' in locals() and dlg.continued():
            _show_warning(MSG_MOVE_FAIL)
        else:
            _show_warning(MSG_OPEN_FAIL)

    finally:
        if record_mode:
            try:
                sfm.SetOperationMode("Pass")
            except Exception:
                pass

        if pushed:
            try:
                sfm.PopSelection()
            except Exception:
                pass


main()
