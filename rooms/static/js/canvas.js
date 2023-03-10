class DrawableCanvasElement {
    constructor(canvasElementId, clearBtnId, onEmitSketch) {
        this.canvasElementId = canvasElementId;
        this.clearBtn = document.getElementById(clearBtnId);
        this.onEmitSketch = onEmitSketch;
        this.paintCanvas = document.getElementById(canvasElementId);
        this.paintContext = this.paintCanvas.getContext("2d");

        this.activeColor = "#9ACD32";
        this.dragging = false;
        this.cursorPoint = { x: 0, y: 0 };

        this.paintCanvas.onmousedown = (e) => { this.onMouseDownHandler(e); };
        this.paintCanvas.onmouseup = (e) => { this.onMouseUpHandler(e); };
        this.paintCanvas.onmouseout = (e) => { this.onMouseUpHandler(e); };
        this.paintCanvas.onmousemove = (e) => { this.onMouseMoveHandler(e); };
        this.clearBtn.onclick = (e) => { this.clearCanvas(e); };
                         
        const canvas = this.paintCanvas;

        document.body.addEventListener("touchstart", (e) => {
            if (e.target == canvas) {
                this.onMouseDownHandler(e); 
            }
        }, false);

        document.body.addEventListener("touchend", (e) => {
            if (e.target == canvas) { 
                this.onMouseUpHandler(e); 
            }
        }, false);
        
        document.body.addEventListener("touchmove", (e) => {
            if (e.target == canvas) { 
                this.onMouseMoveHandler(e); 
            }
        }, false);        
    }

    clearCanvas() {
        const square = document.getElementById(this.canvasElementId);
        this.paintContext.clearRect(0, 0, square.width, square.height);
    }

    onMouseDownHandler(e) {
        document.getElementById(this.canvasElementId).style.cursor = "crosshair";

        this.dragging = true;
        const location = this.getLocationFrom(e);
        this.cursorPoint.x = location.x;
        this.cursorPoint.y = location.y;
    }

    onMouseMoveHandler(e) {
        document.getElementById(this.canvasElementId).style.cursor = "crosshair";
        if(!this.dragging) return;

        const location = this.getLocationFrom(e);
        this.drawing_line(this.activeColor, this.cursorPoint.x, this.cursorPoint.y, location.x, location.y, this.paintContext)
        this.cursorPoint.x = location.x;
        this.cursorPoint.y = location.y;
        //  SENDING DRAWING ON MOUSE MOVE
        this.onEmitSketch(this.toString());
    }

    onMouseUpHandler() {
        this.dragging = false;
        document.getElementById(this.canvasElementId).style.cursor = "default";
    }

    drawing_line(color, x_start, y_start, x_end, y_end, board){
        board.strokeStyle = color;
        board.lineWidth = 1;
        board.beginPath();
        board.moveTo(x_start,y_start);
        board.lineTo(x_end,y_end);
        board.stroke(); 
        board.closePath();
    }

    getLocationFrom(e) {
        const location = { x: 0, y: 0 };

        if (e.constructor.name === "TouchEvent") {            
            const bounds = e.target.getBoundingClientRect();
            const touch = e.targetTouches[0];
            
            location.x = touch.pageX - bounds.left;
            location.y = touch.pageY - bounds.top;
        } else {            
            location.x = e.offsetX;
            location.y = e.offsetY;
        }

        return location;
    }

    toString() {
        return this.paintCanvas.toDataURL("image/png");
    }
};
// /////////////////////////////////////////////////////////////////////////////////////

const make_canvas = () => {
    const canvasContainer = make__div("center-up-flex column");
    
    const canvas = document.createElement('canvas');
    canvas.setAttribute('id', 'canvas');
    canvas.style.backgroundColor = "aliceblue";

    const btnContainer = make__div("flex-between");
    btnContainer.setAttribute('id', 'clearBtnContainer');
    btnContainer.style.gap = '15px';

    const guessBox = make__div('');
    guessBox.setAttribute('id', 'guessBox');

    const guessBoxContainer = make__div('guessBoxContainer');
    guessBoxContainer.appendChild(guessBox);

    const clearBtn = make_button('', 'margin-left: 0 !important', '', t('socketio.clearBtn'), null, "clearBtn");
    btnContainer.append(clearBtn, guessBoxContainer); 

    setImgSize(canvas);
    canvasContainer.append(canvas, btnContainer);
    return canvasContainer;
};


const onEmitSketch = (url) => {
    emittingSketch(url);
};