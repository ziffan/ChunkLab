import { useState, useRef, useCallback } from 'react';

export default function ResizablePanel({
  title,
  children,
  direction = 'vertical',
  defaultHeight = 200,
  defaultWidth = 380,
  minH = 80,
  minW = 200,
  className = '',
}) {
  const isVertical = direction === 'vertical';

  const [height, setHeight] = useState(defaultHeight);
  const [width, setWidth] = useState(defaultWidth);

  const dragging = useRef(false);
  const startRef = useRef(0);
  const sizeRef = useRef(0);

  const onMouseDown = useCallback(
    (e) => {
      e.preventDefault();
      dragging.current = true;
      startRef.current = isVertical ? e.clientY : e.clientX;
      sizeRef.current = isVertical ? height : width;

      const onMouseMove = (e) => {
        if (!dragging.current) return;
        const delta = (isVertical ? e.clientY : e.clientX) - startRef.current;
        if (isVertical) {
          setHeight(Math.max(minH, sizeRef.current + delta));
        } else {
          setWidth(Math.max(minW, sizeRef.current + delta));
        }
      };

      const onMouseUp = () => {
        dragging.current = false;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    },
    [isVertical, height, width, minH, minW]
  );

  const style = isVertical
    ? { height: `${height}px` }
    : { width: `${width}px` };

  const handleClass = isVertical
    ? 'h-2 cursor-row-resize flex items-center justify-center hover:bg-slate-600 rounded-b-lg'
    : 'w-2 cursor-col-resize flex items-center justify-center hover:bg-slate-600 rounded-r-lg';

  const handleInner = isVertical
    ? 'w-8 h-[2px] bg-slate-500 rounded-full'
    : 'h-8 w-[2px] bg-slate-500 rounded-full';

  return (
    <div
      className={`bg-slate-800 border border-slate-700 rounded-lg flex ${isVertical ? 'flex-col' : 'flex-row'} ${className}`}
      style={style}
    >
      <div className={`flex flex-col flex-1 min-h-0 ${isVertical ? '' : 'min-w-0 overflow-hidden'}`}>
        {title && (
          <div className="flex items-center justify-between px-3 pt-2 pb-1 flex-shrink-0">
            <div className="text-[12px] uppercase text-slate-400">{title}</div>
          </div>
        )}
        <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 pb-1">
          {children}
        </div>
      </div>
      <div onMouseDown={onMouseDown} className={`flex-shrink-0 ${handleClass} transition-colors`}>
        <div className={handleInner} />
      </div>
    </div>
  );
}
