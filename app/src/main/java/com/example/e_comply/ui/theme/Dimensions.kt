package com.example.e_comply.ui.theme

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Responsive dimension system for dynamic padding and sizing.
 *
 * Adapts to screen size:
 *   Compact  (< 360dp)  — small phones
 *   Medium   (360–600dp) — standard phones
 *   Expanded (> 600dp)   — tablets / foldables
 */
data class Dimensions(
    val screenPaddingH: Dp,
    val screenPaddingV: Dp,
    val cardPadding: Dp,
    val cardRadius: Dp,
    val itemSpacing: Dp,
    val sectionSpacing: Dp,
    val iconSize: Dp,
    val iconSizeLg: Dp,
    val avatarSize: Dp,
    val buttonHeight: Dp,
    val chipHeight: Dp,
)

val CompactDimensions = Dimensions(
    screenPaddingH = 12.dp,
    screenPaddingV = 8.dp,
    cardPadding = 12.dp,
    cardRadius = 14.dp,
    itemSpacing = 8.dp,
    sectionSpacing = 16.dp,
    iconSize = 20.dp,
    iconSizeLg = 40.dp,
    avatarSize = 56.dp,
    buttonHeight = 44.dp,
    chipHeight = 28.dp,
)

val MediumDimensions = Dimensions(
    screenPaddingH = 16.dp,
    screenPaddingV = 12.dp,
    cardPadding = 16.dp,
    cardRadius = 18.dp,
    itemSpacing = 12.dp,
    sectionSpacing = 20.dp,
    iconSize = 24.dp,
    iconSizeLg = 48.dp,
    avatarSize = 72.dp,
    buttonHeight = 52.dp,
    chipHeight = 32.dp,
)

val ExpandedDimensions = Dimensions(
    screenPaddingH = 24.dp,
    screenPaddingV = 16.dp,
    cardPadding = 20.dp,
    cardRadius = 22.dp,
    itemSpacing = 14.dp,
    sectionSpacing = 24.dp,
    iconSize = 28.dp,
    iconSizeLg = 56.dp,
    avatarSize = 88.dp,
    buttonHeight = 56.dp,
    chipHeight = 36.dp,
)

@Composable
fun rememberDimensions(): Dimensions {
    val config = LocalConfiguration.current
    val screenWidthDp = config.screenWidthDp
    return when {
        screenWidthDp < 360 -> CompactDimensions
        screenWidthDp < 600 -> MediumDimensions
        else -> ExpandedDimensions
    }
}
