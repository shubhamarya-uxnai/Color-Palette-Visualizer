import {
  Button as DSButton,
  IconButton as DSIconButton,
  InputField as DSInputField,
  Selection as DSSelection,
  Chip as DSChip,
  ProgressBar as DSProgressBar,
  ProgressPie as DSProgressPie,
  ProgressDonut as DSProgressDonut,
  Loader as DSLoader,
  Loaders as DSLoaders,
  SegmentedChild as DSSegmentedChild,
  StepperChild as DSStepperChild,
  SegmentedProgress as DSSegmentedProgress,
  Stepper as DSStepper,
} from "@ba-design-system/react";
export function ActionButton({ variant = "ghost", size = "small", disabled, children, ...props }) {
  return <DSButton {...props} Type={variant === "primary" ? "Primary" : variant === "default" ? "Default" : "Ghost"} Size={size === "large" ? "Large" : "Small"} Enabled={!disabled} {...{ "Leading Icon": false, "Tailing Icon": false }}>{children}</DSButton>;
}
export function IconAction({ variant = "ghost", size = "small", disabled, icon, ...props }) {
  return <DSIconButton {...props} Type={variant === "primary" ? "Primary" : variant === "default" ? "Default" : "Ghost"} Size={size === "large" ? "Large" : "Small"} Enabled={!disabled} icon={icon} />;
}
export const Field = DSInputField;
export const Choice = DSSelection;
export const StatusChip = DSChip;
export const ProgressBar = DSProgressBar;
export const ProgressPie = DSProgressPie;
export const ProgressDonut = DSProgressDonut;
export const Loader = DSLoader;
export const Loaders = DSLoaders;
export const SegmentedChild = DSSegmentedChild;
export const StepperChild = DSStepperChild;
export const SegmentedProgress = DSSegmentedProgress;
export const Stepper = DSStepper;

