import { Button as DSButton, IconButton as DSIconButton, InputField as DSInputField, Selection as DSSelection, Chip as DSChip } from "@ba-design-system/react";
export function ActionButton({ variant = "ghost", size = "small", disabled, children, ...props }) {
  return <DSButton {...props} Type={variant === "primary" ? "Primary" : variant === "default" ? "Default" : "Ghost"} Size={size === "large" ? "Large" : "Small"} Enabled={!disabled} {...{ "Leading Icon": false, "Tailing Icon": false }}>{children}</DSButton>;
}
export function IconAction({ variant = "ghost", size = "small", disabled, icon, ...props }) {
  return <DSIconButton {...props} Type={variant === "primary" ? "Primary" : variant === "default" ? "Default" : "Ghost"} Size={size === "large" ? "Large" : "Small"} Enabled={!disabled} icon={icon} />;
}
export const Field = DSInputField;
export const Choice = DSSelection;
export const StatusChip = DSChip;
