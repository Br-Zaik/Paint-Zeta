from pathlib import Path

root = Path("extracted/PaintZeta")
main = root / "app/src/main/java/com/pacco/animecut/MainActivity.java"
canvas = root / "app/src/main/java/com/pacco/animecut/view/CanvasView.java"
m = main.read_text(encoding="utf-8")
c = canvas.read_text(encoding="utf-8")

def rep(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

# Especial: reducir acumulacion y deformaciones largas.
c = rep(c,
    'if (mode == MODE_LIQUIFY) step = Math.max(1f, brushRadius * 0.22f);',
    'if (mode == MODE_LIQUIFY) step = Math.max(1.5f, brushRadius * 0.34f);',
    'step')
c = rep(c,
    'n = Math.min(n, 64);',
    'n = Math.min(n, mode == MODE_LIQUIFY ? 32 : 64);',
    'stamps')
c = rep(c,
    'float maxDrag = Math.max(1f, r * (special ? .18f : .14f));',
    'float maxDrag = Math.max(1f, r * (special ? .10f : .14f));',
    'maxdrag')
c = rep(c,
    'float gainMax = special ? (.45f + 1.35f * base) : (.35f + .65f * base);',
    'float gainMax = special ? (.22f + .58f * base) : (.35f + .65f * base);',
    'gainmax')
c = rep(c,
    'float gain = (.45f + 1.35f * base) * fall;',
    'float gain = (.22f + .58f * base) * fall;',
    'gain')
c = rep(c,
    'float k = 1f + (.10f + .30f * base) * fall;',
    'float k = 1f + (.06f + .18f * base) * fall;',
    'contract')
c = rep(c,
    'float k = Math.max(.48f, 1f - (.09f + .27f * base) * fall);',
    'float k = Math.max(.68f, 1f - (.06f + .18f * base) * fall);',
    'expand')
c = rep(c,
    'float a = (.10f + .42f * base) * fall;',
    'float a = (.06f + .22f * base) * fall;',
    'swirl')
c = rep(c,
    'blend = Math.min(1f, fall * sel * (.88f + .12f * base));',
    'blend = Math.min(1f, fall * sel * (.96f + .04f * base));',
    'blend')

# Transformar: quitar los cuatro +/- iguales de la malla.
old_transform = '''            if (tt == 2) {
                // Filas y columnas se controlan por separado. Permite cuadros mas
                // pequenos donde hace falta precision sin llenar toda la malla.
                bar.addView(iconButton(R.drawable.ic_sub, "Menos columnas", new Runnable() {
                    public void run() { canvas.changeTransformGridCols(-1); updateUi(); }
                }));
                bar.addView(iconButton(R.drawable.ic_add, "Mas columnas", new Runnable() {
                    public void run() { canvas.changeTransformGridCols(1); updateUi(); }
                }));
                bar.addView(iconButton(R.drawable.ic_sub, "Menos filas", new Runnable() {
                    public void run() { canvas.changeTransformGridRows(-1); updateUi(); }
                }));
                bar.addView(iconButton(R.drawable.ic_add, "Mas filas", new Runnable() {
                    public void run() { canvas.changeTransformGridRows(1); updateUi(); }
                }));
            }
'''
new_transform = '''            if (tt == 2) {
                // Malla simple: un solo - y un solo + para filas y columnas.
                bar.addView(iconButton(R.drawable.ic_sub, "Malla menos densa", new Runnable() {
                    public void run() { canvas.changeTransformGrid(-1); updateUi(); }
                }));
                TextView gridInfo = new TextView(this);
                gridInfo.setText(canvas.getTransformGridCols() + " x " + canvas.getTransformGridRows());
                gridInfo.setTextColor(0xFFE6E6E6);
                gridInfo.setTextSize(12f);
                gridInfo.setGravity(android.view.Gravity.CENTER);
                gridInfo.setPadding(dp(5), 0, dp(5), 0);
                bar.addView(gridInfo, new LinearLayout.LayoutParams(dp(54), dp(44)));
                bar.addView(iconButton(R.drawable.ic_add, "Malla mas densa", new Runnable() {
                    public void run() { canvas.changeTransformGrid(1); updateUi(); }
                }));
            }
'''
m = rep(m, old_transform, new_transform, 'transform-ui')

# Referencia de color visible directamente en Capas.
marker = '''        addAction(bar, R.drawable.ic_dup, "Duplicar", new Runnable() {
            public void run() {
                canvas.duplicateActive();
                afterLayerOp();
            }
        });
'''
insert = marker + '''        addAction(bar, R.drawable.ic_layer_add, "Ref. color", new Runnable() {
            public void run() {
                requestColorReference(new ColorPickTarget() {
                    @Override public void onColor(int color) {
                        canvas.setColor(color | 0xFF000000);
                        canvas.showHud("Color tomado de la referencia");
                        updateUi();
                    }
                });
            }
        });
'''
m = rep(m, marker, insert, 'reference')

# Mensajes claros para los tres modos de Transformar.
m = rep(m,
    'public void run() { canvas.setTransformType(0); updateUi(); }',
    'public void run() { canvas.setTransformType(0); canvas.showHud("Mover / escalar / girar"); updateUi(); }',
    'free')
m = rep(m,
    'public void run() { canvas.setTransformType(1); updateUi(); }',
    'public void run() { canvas.setTransformType(1); canvas.showHud("Perspectiva: mueve las 4 esquinas"); updateUi(); }',
    'persp')
m = rep(m,
    'public void run() { canvas.setTransformType(2); updateUi(); }',
    'public void run() { canvas.setTransformType(2); canvas.showHud("Malla: arrastra los puntos para deformar"); updateUi(); }',
    'mesh')

main.write_text(m, encoding="utf-8")
canvas.write_text(c, encoding="utf-8")
print("Paint Zeta v8.9 patch OK")
