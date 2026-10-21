# BA Design System integration

The React source uses the shared BA React package through one adapter in `react-app/src/ui/components.jsx`, following the Gradient Creator pattern. Buttons and icon buttons map product variants and sizes to BA component props there. The app imports BA component styles and the shared consumer CSS during its Vite build. No local design-system implementation is maintained in this repository.

The default build resolves the sibling `va-design-system` checkout. `BA_DESIGN_SYSTEM_DIR` can point to another compatible checkout.
