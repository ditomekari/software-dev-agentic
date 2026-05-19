# MekariPixel Flutter Catalog

**Platform:** Flutter only. Non-Flutter platforms: N/A.
**Import:** `package:mekari_pixel/mekari_pixel.dart`
**Prefix:** `Mp` (e.g. `MpButton`, `MpAvatar`, `MpListTileX`)
**Sync:** re-run `temp-dir/extract_catalog.py` on MekariPixel version bump.

Total widgets: 228

---

## Atoms

### MpActionText
- **Category:** `atoms/action_text`
- **Description:** A Text which triggered an action when tapped.
- **Key params:** `onTap`, `style`, `semantics`
- **Variants:** `MpActionText.value()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17806-4384

### MpAvatarError
- **Category:** `atoms/avatar`
- **Description:** Mekari Pixel - Avatar Error widget of [MpAvatar]
- **Key params:** `icon`, `size`, `color`, `semantics`

### MpBackButton
- **Category:** `atoms/icon_button`
- **Description:** An [MpIconButton] widget with a "back" icon. When pressed, the close button calls [Navigator.maybePop] to return to the previous route.
- **Key params:** `color`, `onPressed`, `tooltip`, `semantics`

### MpBadge
- **Category:** `atoms/badge`
- **Description:** Mekari Mobile Kit - Badge
- **Key params:** `text`, `icon`, `style`, `size`, `semantics`
- **Variants:** `MpBadge.informative()`, `MpBadge.neutral()`, `MpBadge.notice()`, `MpBadge.positive()`, `MpBadge.negative()`, `MpBadge.informativeStatus()`, `MpBadge.neutralStatus()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17337-1048

### MpButton
- **Category:** `atoms/button`
- **Description:** Mekari Mobile Kit Button.
- **Key params:** `label`, `icon`, `onPressed`, `onLongPress`, `style`, `size`, `semantics`
- **Variants:** `MpButton.primary()`, `MpButton.secondary()`, `MpButton.tertiary()`, `MpButton.ghost()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17323-74724

### MpButtonIcon
- **Category:** `atoms/button_icon`
- **Description:** Mekari Mobile Kit - Button Icon.
- **Key params:** `icon`, `style`, `padding`, `onPressed`, `onLongPress`, `tooltip`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=6940-60334

### MpCheckbox
- **Category:** `atoms/checkbox`
- **Description:** Mekari Mobile Kit - Checkbox.
- **Key params:** `value`, `onTap`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5308&t=c8IIoGc1ZdE8vXIF-0

### MpChip
- **Category:** `atoms/chips`
- **Description:** Mekari Mobile Kit - Chip
- **Key params:** `text`, `style`, `leading`, `trailing`, `onTap`, `semantics`
- **Variants:** `MpChip.outline()`, `MpChip.duoTone()`, `MpChip.fill()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17403-50814&t=2id5EKrhfnUsvyg3-4

### MpCloseButton
- **Category:** `atoms/icon_button`
- **Description:** An [MpIconButton] widget with a "close" icon. When pressed, the close button calls [Navigator.maybePop] to return to the previous route.
- **Key params:** `color`, `onPressed`, `tooltip`, `semantics`

### MpDatePickerCell
- **Category:** `atoms/date_picker/cell`
- **Description:** Core widget for Date Picker View Components <br/> This widget will display [DateTime] in an interactive cell / box <br/> Can be styled by using [MpDatePickerCellStyle]
- **Key params:** `date`, `height`, `width`, `style`, `onDateSelected`, `locale`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=2526%3A11105&t=dPUEec95KUZK0BTx-4

### MpFloatingActionButton
- **Category:** `atoms/floating_action_button`
- **Description:** A widget that displays Floating Action Button.
- **Key params:** `key`, `icon`, `label`, `style`, `transitionController`, `transition`, `onPressed`, `semantics`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=17587-13389&t=AvL1D1iHweZxKwW9-0

### MpHeartBeatIcon
- **Category:** `atoms/icon`
- **Description:** A [MpIcon] with `Heart Beat` (Pulses) animation.
- **Key params:** `icon`, `color`, `size`, `onTap`, `blendMode`, `customColor`

### MpHomeIndicator
- **Category:** `atoms/home_indicator`
- **Description:** A widget that displays home indicator.
- **Key params:** `isAndroid`, `indicatorColor`, `backgroundColor`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=45%3A1144&t=NuKpAmbmPNewhYsQ-0

### MpIcon
- **Category:** `atoms/icon`
- **Description:** A widget that displays an icon from assets folder or network images. Support SVG, PNG, JPG, GIF and other formats supported by flutter.
- **Key params:** `filepath`, `size`, `color`, `blendMode`, `onTap`, `tooltip`, `customColor`, `semantics`

### MpIconButton
- **Category:** `atoms/icon_button`
- **Description:** [MpIconButton] are commonly used in the [AppBar.actions] field, but they can be used in many other places as well.
- **Key params:** `icon`, `iconSize`, `onPressed`, `onLongPress`, `color`, `disabledColor`, `highlightColor`, `splashColor`

### MpImage
- **Category:** `atoms/image`
- **Description:** A widget that displays an image from assets folder or network images. Support SVG, PNG, JPG, GIF and other formats supported by flutter.
- **Key params:** `filepath`, `theme`, `onTap`, `semantics`

### MpImageError
- **Category:** `atoms/image`
- **Description:** Default error widget of [MpImage]
- **Key params:** `error`, `height`, `width`

### MpImageLoading
- **Category:** `atoms/image`
- **Description:** Default placeholder of [MpImage]
- **Key params:** `color`, `lineColor`, `height`, `width`

### MpMultiColorIcon
- **Category:** `atoms/icon/multi_color`
- **Description:** A widget that displays a customable multi color svg icon from assets. Mainly used for multicolored like [duotone] variant svg asset icons.
- **Key params:** `filepath`, `size`, `onTap`, `tooltip`, `customColor`, `semantics`

### MpRotationIcon
- **Category:** `atoms/icon`
- **Key params:** `icon`, `size`, `rotationSpeed`, `color`, `semantics`, `size`, `rotationSpeed`, `color`

### MpSlideToAction
- **Category:** `atoms/slide_to_action`
- **Description:** Mekari Mobile Kit - Slide To Action
- **Key params:** `sliderCaption`, `onSubmitCallback`, `isFinished`, `slideCaptionStyle`, `initialSliderColor`, `activeSliderColor`, `activeSliderBackgroundColor`, `inactiveSliderBackgroundColor`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18084-55692&node-type=frame&t=Zh1Srnn2w9ALX8gY-0

### MpStatusBar
- **Category:** `atoms/status_bar`
- **Description:** Mekari Mobile Kit Status Bar
- **Key params:** `time`, `icons`, `isAndroid`, `backgroundColor`, `foregroundColor`, `semantics`, `time`, `iconThemeData`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=31%3A291&t=FyL16Qn3He2YbGoq-0

### MpTag
- **Category:** `atoms/tag`
- **Description:** Mekari Mobile Kit - Tag
- **Key params:** `label`, `onPressed`, `style`, `semantics`
- **Variants:** `MpTag.error()`, `MpTag.disable()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5225-38439&mode=design&t=ryYH3ILcjc9Zvo0a-4

### MpTextField
- **Category:** `atoms/text_field`
- **Description:** Mekari Mobile Kit - Textfield.
- **Key params:** `mainKey`, `controller`, `focusNode`, `label`, `hint`, `error`, `helper`, `textInputAction`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=86%3A2099&t=NuKpAmbmPNewhYsQ-0

### MpToggle
- **Category:** `atoms/toggle`
- **Description:** Mekari Mobile Kit - Toogle
- **Key params:** `value`, `style`, `onChanged`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=448%3A6576&t=nPrga1tGl9WiRGaY-0

---

## Components

### MpAccordionTimeline
- **Category:** `components/timeline`
- **Description:** Mekari Pixel - Timeline (Variant: Accordion)
- **Key params:** `label`, `icon`, `iconCollapse`, `labelStyle`, `caption`, `captionStyle`, `badge`, `accordionContent`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5343-46805&mode=design&t=COdbyxlFRHGuavvx-4

### MpAlignmentToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Toggle text alignment (Left, Center, Right) in the text editor.
- **Key params:** `controller`, `tooltip`, `style`, `semantics`
- **Variants:** `MpAlignmentToolbarButton.basic()`

### MpAttachmentToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Insert files to text editor's document from device storage.
- **Key params:** `icon`, `tooltip`, `style`, `onFilePickCallback`, `semantics`
- **Variants:** `MpAttachmentToolbarButton.basic()`

### MpAvatarBottomSheetContent
- **Category:** `components/bottom_sheet`
- **Description:** Mekari Mobile Kit - Bottomsheet - Variant: Avatar
- **Key params:** `title`, `labelButton`, `content`, `onTapClose`, `onTapButton`, `actions`, `actionSpacing`, `semantics`

### MpAvatarCheckboxList
- **Category:** `components/checkbox`
- **Description:** Mekari Checkbox Button List - Variant: Avatar
- **Key params:** `values`, `onChanged`, `style`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5309&t=PLJMony4dHpmREqs-0

### MpAvatarGroup
- **Category:** `components/avatar_group`
- **Description:** Mekari Mobile Kit Avatar Group.
- **Key params:** `size`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=13950-51798&t=iwZtQ6DFoWNJrx1M-4

### MpBanner
- **Category:** `components/banner`
- **Description:** Mekari Mobile Kit - Banner
- **Key params:** `icon`, `title`, `titleRich`, `message`, `messageRich`, `style`, `suffix`, `actions`
- **Variants:** `MpBanner.info()`, `MpBanner.warning()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=1959%3A24743&t=zrV67Ozpejx6d8zk-0

### MpBannerAction
- **Category:** `components/banner`
- **Description:** Display action at the bottom side of [MpBanner]
- **Key params:** `text`, `textStyle`, `onTap`, `semantics`, `text`, `textStyle`, `onTap`, `semantics`

### MpBlankSlate
- **Category:** `components/blank_slate`
- **Description:** Mekari Mobile Kit - Blank Slate
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=44%3A827&t=cebsrVLXNB3dX47O-0

### MpBottomNavBar
- **Category:** `components/bottom_nav_bar`
- **Description:** Mekari Bottom Navigation Bar
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=44%3A827&t=cebsrVLXNB3dX47O-0

### MpBroadcast
- **Category:** `components/broadcast`
- **Description:** Mekari Mobile Kit Broadcast.
- **Key params:** `label`, `description`, `leading`, `trailing`, `style`, `semantics`
- **Variants:** `MpBroadcast.important()`, `MpBroadcast.critical()`, `MpBroadcast.news()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=915%3A24757&t=1tCrAZMm1YM9oh2Y-0

### MpBroadcastArea
- **Category:** `components/broadcast`
- **Key params:** `broadcast`, `topPadding`, `defaultStatusBarColor`, `defaultStatusBarBrightness`, `child`

### MpBubbleChatAttachment
- **Category:** `components/bubble_chat`
- **Description:** Mekari Mobile Kit - Bubble Chat Attachment A Bubble Chat Attachment
- **Key params:** `backgroundColor`, `margin`, `padding`, `borderRadius`, `chatText`, `chatTextStyle`, `timestamp`, `timestampStyle`
- **Variants:** `MpBubbleChatAttachment.imageDirect()`, `MpBubbleChatAttachment.imageSelf()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatAttachmentItemAudio
- **Category:** `components/bubble_chat/part/attachment`
- **Description:** Mekari Mobile Kit - Attachment Audio A  Attachment Audio.
- **Key params:** `audioUrl`, `audioSize`, `backgroundColor`, `borderRadius`, `thumbnail`, `thumbnailBackgroundColor`, `onDownloadTap`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatAttachmentItemFile
- **Category:** `components/bubble_chat/part/attachment`
- **Description:** Mekari Mobile Kit - Attachment File A  Attachment File.
- **Key params:** `fileName`, `fileNameTextStyle`, `fileNameColor`, `fileInfo`, `fileInfoStyle`, `fileInfoColor`, `backgroundColor`, `borderRadius`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatAttachmentItemImage
- **Category:** `components/bubble_chat/part/attachment`
- **Description:** Mekari Mobile Kit - Attachment Image A  Attachment Image.
- **Key params:** `images`, `theme`, `width`, `padding`, `height`, `onTap`, `onMoreImageTap`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatAttachmentItemVideo
- **Category:** `components/bubble_chat/part/attachment`
- **Description:** Mekari Mobile Kit - Attachment Video A  Attachment Video.
- **Key params:** `videoUrl`, `onTap`, `semantics`, `borderRadius`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatBasic
- **Category:** `components/bubble_chat`
- **Description:** Mekari Mobile Kit - Bubble Chat Basic A Bubble Chat Basic
- **Key params:** `chatText`, `chatTextStyle`, `timestamp`, `timestampStyle`, `foregroundColor`, `read`, `readIndicator`, `backgroundColor`
- **Variants:** `MpBubbleChatBasic.self()`, `MpBubbleChatBasic.direct()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatBubble
- **Category:** `components/bubble_chat/part`
- **Description:** Mekari Mobile Kit - Bubble A Bubble.
- **Key params:** `width`, `height`, `color`, `margin`, `padding`, `child`, `borderRadius`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatGroup
- **Category:** `components/bubble_chat`
- **Description:** Mekari Mobile Kit - Bubble Chat Group A Bubble Chat Group
- **Key params:** `name`, `children`, `nameStyle`, `nameColor`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatProfile
- **Category:** `components/bubble_chat/part`
- **Description:** Mekari Mobile Kit - Profile A Profile.
- **Key params:** `name`, `nameStyle`, `nameColor`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatReply
- **Category:** `components/bubble_chat`
- **Description:** Mekari Mobile Kit - Bubble Chat Reply A Bubble Chat Reply
- **Variants:** `MpBubbleChatReply.textSelf()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatReplyItem
- **Category:** `components/bubble_chat/part`
- **Description:** Mekari Mobile Kit - ReplyItem A ReplyItem.
- **Key params:** `replyText`, `replyTextStyle`, `replyTextColor`, `replyCaption`, `replyCaptionStyle`, `replyCaptionColor`, `backgroundColor`, `borderRadius`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpBubbleChatTimestamp
- **Category:** `components/bubble_chat/part`
- **Description:** Mekari Mobile Kit - Timestamp A Timestamp
- **Key params:** `timestamp`, `timestampStyle`, `timestampColor`, `read`, `readIndicator`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5454%3A53419&mode=dev

### MpChatDivider
- **Category:** `components/bubble_chat/part`
- **Key params:** `lineColor`, `margin`, `semantics`

### MpCheckboxBottomSheetContent
- **Category:** `components/bottom_sheet`
- **Description:** Mekari Mobile Kit - Bottomsheet - Variant: Checkbox
- **Key params:** `title`, `labelButton`, `content`, `style`, `onTapClose`, `onTapButton`, `actions`, `actionSpacing`

### MpCheckboxList
- **Category:** `components/checkbox`
- **Description:** Mekari Checkbox List - Variant: Basic
- **Key params:** `values`, `onChanged`, `style`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5309&t=PLJMony4dHpmREqs-0

### MpContextualMenu
- **Category:** `components/contextual_menu`
- **Description:** Mekari Mobile Kit - Contextual Menu A Contextual Menu.
- **Key params:** `child`, `previewChild`, `verticalMenuItems`, `horizontalMenuItems`
- **Variants:** `MpContextualMenu.vertical()`, `MpContextualMenu.horizontal()`, `MpContextualMenu.verticalHorizontal()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5824-58261&mode=design&t=TbOMGAZc5bUVGJkt-0

### MpContextualMenuItem
- **Category:** `components/contextual_menu`
- **Description:** Mekari Mobile Kit - Contextual Menu (Part: item) An item for contextual menu button icon.
- **Key params:** `title`, `titleTextStyle`, `subtitle`, `subtitleTextStyle`, `icon`, `iconColor`, `onTap`, `customBorder`
- **Variants:** `MpContextualMenuItem.verticalSectionTitle()`, `MpContextualMenuItem.verticalActionItem()`, `MpContextualMenuItem.horizontal()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5824-58360&mode=design&t=0BNffzg67u2AcnLS-0

### MpCountryPicker
- **Category:** `components/country_picker`
- **Key params:** `country`, `onSelectionChanged`, `languageCode`, `bottomsheetTitle`, `semantics`

### MpCountryPickerBottomSheet
- **Category:** `components/country_picker`
- **Key params:** `title`, `languageCode`, `semantics`

### MpCustomKeyboard
- **Category:** `components/custom_keyboard`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Custom Keyboard.
- **Key params:** `actionBuilder`, `onTapNumber`, `onTapBackspace`, `textStyle`, `iconColor`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=2570-12372

### MpDatePickerField
- **Category:** `components/date_picker`
- **Description:** Mekari Mobile Kit - Date Picker Field
- **Key params:** `selectedDate`, `firstDate`, `lastDate`, `events`, `sheetTitleLabel`, `stringLibrary`, `focusNode`, `label`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17475-22286&t=OxbAmb5Gcttt4wKm-4

### MpDatePickerHeader
- **Category:** `components/date_picker`
- **Key params:** `semantics`, `title`, `clearButton`, `saveButton`

### MpDatePickerMenu
- **Category:** `components/date_picker/body`
- **Description:** Mekari Mobile Kit: Date Picker Menu Selection <br/> This component will show a menu to display and manipulate [DateTime] <br/>
- **Key params:** `label`, `labelStyle`, `isMenuOpened`, `onMenuPressed`, `onPrevPressed`, `onNextPressed`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=2542-12549&t=crHQWqZtF43eji1F-4

### MpDatePickerRangeField
- **Category:** `components/date_picker`
- **Description:** Mekari Mobile Kit - Date Picker Field
- **Key params:** `dateRange`, `firstDate`, `lastDate`, `events`, `sheetTitleLabel`, `stringLibrary`, `focusNode`, `label`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17475-22286&t=OxbAmb5Gcttt4wKm-4

### MpDatePickerRangeInfo
- **Category:** `components/date_picker/body`
- **Description:** Mekari Mobile Kit: Range Info Component <br/> This component will information about [DateTimeRange] <br/>
- **Key params:** `dateRange`, `stringLibrary`, `locale`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4125-28163&t=crHQWqZtF43eji1F-4

### MpDayDatePickerBody
- **Category:** `components/date_picker/body/day`
- **Description:** Mekari Mobile Kit: Date Picker Day Picker <br/> This component will show all visible days in the following month <br/> User able to select date inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `labelStyle`, `cellStyle`, `events`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-27401&t=crHQWqZtF43eji1F-4

### MpDayDatePickerBodyHeader
- **Category:** `components/date_picker/body/day`
- **Description:** Mekari Mobile Kit: Date Picker Day Header <br/> This component will show table of weekdays start from sunday <br/>
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=2542-11477&t=crHQWqZtF43eji1F-4

### MpDayDatePickerBodyView
- **Category:** `components/date_picker/body/day`
- **Description:** Mekari Mobile Kit: Date Picker Day View <br/> This component will show all visible days in the following month <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `cellStyle`, `events`, `onDateSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-27401&t=crHQWqZtF43eji1F-4

### MpDayDatePickerRangeBody
- **Category:** `components/date_picker/body/day`
- **Description:** Mekari Mobile Kit: Date Picker Day Range Picker <br/> This component will show all visible days in the following month <br/> User able to select date range inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `dateRange`, `labelStyle`, `cellStyle`, `events`, `onDateRangeSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-27401&t=crHQWqZtF43eji1F-4

### MpDayDatePickerRangeSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker Date Range Picker - Day - Sheet <br/> This template will show all visible days in the following month in a sheet <br/> User able to select date range inside this sheet <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `dateRange`, `menuStyle`, `cellStyle`, `events`, `titleLabel`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=837-21606&t=crHQWqZtF43eji1F-4

### MpDayDatePickerSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker - Day - Sheet <br/> This template will show all visible days in the following month in a sheet <br/> User able to select date inside this sheet <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `menuStyle`, `cellStyle`, `events`, `titleLabel`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=2526-11359&t=crHQWqZtF43eji1F-4

### MpDoubleListTileXContent
- **Category:** `components/list_tile_x`
- **Key params:** `label`, `caption`, `labelStyle`, `captionStyle`, `overflow`, `textAlign`

### MpFilter
- **Category:** `components/filter`
- **Description:** Mekari Mobile Kit - Filter
- **Key params:** `tags`, `selectedStyle`, `unselectedStyle`, `buttonLabel`, `buttonForegroundColor`, `buttonIcon`, `onTapFilter`, `onTapTag`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=9273-26004&t=coQA4b63Bj2T22kR-0

### MpFilterButton
- **Category:** `components/filter`
- **Description:** Mekari Mobile Kit - Filter Button
- **Key params:** `label`, `icon`, `onTap`, `foregroundColor`, `borderColor`, `semantics`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=9273-26004&t=coQA4b63Bj2T22kR-0

### MpFullDatePickerBody
- **Category:** `components/date_picker/body/full`
- **Description:** Mekari Mobile Kit: Date Picker Full Picker <br/> This component will show expanded view of date picker that can be scrollable <br/> User able to select date inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `cellStyle`, `events`, `onDateSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-29919&t=crHQWqZtF43eji1F-4

### MpFullDatePickerBodyView
- **Category:** `components/date_picker/body/full`
- **Description:** Mekari Mobile Kit: Date Picker Full View <br/> This component will show expanded view of date picker that can be scrollable <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `cellStyle`, `events`, `onDateSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-29642&t=crHQWqZtF43eji1F-4

### MpFullDatePickerRangeBody
- **Category:** `components/date_picker/body/full`
- **Description:** Mekari Mobile Kit: Date Picker Full Range Picker <br/> This component will show expanded view of date picker that can be scrollable <br/> User able to select date range inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `dateRange`, `cellStyle`, `events`, `onDateRangeSelected`, `locale`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-30102&t=crHQWqZtF43eji1F-4

### MpFullDatePickerRangeSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Range Picker - Full - Sheet <br/> This template will show expanded view of date picker that can be scrollable in a sheet <br/> User able to select date range inside this sheet <br/>
- **Key params:** `firstDate`, `lastDate`, `dateRange`, `cellStyle`, `events`, `titleLabel`, `onClearButtonPressed`, `onSaveButtonPressed`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=837-21606&t=crHQWqZtF43eji1F-4

### MpFullDatePickerSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker - Full - Sheet <br/> This template will show expanded view of date picker that can be scrollable in a sheet <br/> User able to select date inside this sheet <br/>
- **Key params:** `firstDate`, `lastDate`, `selectedDate`, `cellStyle`, `events`, `titleLabel`, `onClearButtonPressed`, `onSaveButtonPressed`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4101-29919&t=crHQWqZtF43eji1F-4

### MpHeadingToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Toggle heading styles (Normal, H1, H2) in the text editor.
- **Key params:** `controller`, `tooltip`, `style`, `semantics`
- **Variants:** `MpHeadingToolbarButton.basic()`

### MpIconLeftCheckboxList
- **Category:** `components/checkbox`
- **Description:** Mekari Checkbox List - Variant: Icon Left
- **Key params:** `values`, `onChanged`, `style`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5309&t=PLJMony4dHpmREqs-0

### MpImageToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Insert images to text editor's document either from camera or gallery.
- **Key params:** `icon`, `tooltip`, `style`, `onImagePickCallback`, `semantics`
- **Variants:** `MpImageToolbarButton.basic()`

### MpIndentToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Toggle text indentation levels in the text editor.
- **Key params:** `controller`, `tooltip`, `style`, `semantics`
- **Variants:** `MpIndentToolbarButton.basic()`

### MpInputTag
- **Category:** `components/input_tag`
- **Description:** Mekari Mobile Kit - Input Tags
- **Key params:** `label`, `onTap`, `style`, `suffixIcon`, `errorText`, `padding`, `semantics`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17513-15338

### MpInputTagCreate
- **Category:** `components/input_tag`
- **Description:** Mekari Mobile Kit - Input Tags - Create
- **Key params:** `label`, `onSelectionChanged`, `validator`, `selectedItems`, `padding`, `separator`, `style`, `suffixIcon`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5225-40879

### MpLinkToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Insert link into text editor. The link will be clickable to open a webview. It is also possible to customize the action using [MpTextEditor.onTapLink].
- **Key params:** `controller`, `icon`, `tooltip`, `style`, `onPressed`, `semantics`
- **Variants:** `MpLinkToolbarButton.basic()`

### MpLoadingAnimation
- **Category:** `components/loading_animation`
- **Description:** Mekari Mobile Kit - Loading Animation
- **Key params:** `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=6416-55659&mode=design&t=DPQylcbClrKUqjVO-0

### MpMentionToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Insert names into text editor. The mentioned names will be clickable to open a webview. It is also possible to customize the action using [MpTextEditor.onTapLink].
- **Key params:** `controller`, `icon`, `tooltip`, `style`, `onPressed`, `users`, `semantics`
- **Variants:** `MpMentionToolbarButton.basic()`

### MpMonthDatePickerBody
- **Category:** `components/date_picker/body/month`
- **Description:** Mekari Mobile Kit: Date Picker Month Picker <br/> This component will show all visible months in the following year <br/> User able to select month inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `labelStyle`, `cellStyle`, `events`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30987&t=ARnxQ2jFK0WP3Ih7-4

### MpMonthDatePickerBodyView
- **Category:** `components/date_picker/body/month`
- **Description:** Mekari Mobile Kit: Date Picker Month View <br/> This component will show all visible months in the following year <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `cellStyle`, `events`, `onDateSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30987&t=ARnxQ2jFK0WP3Ih7-4

### MpMonthDatePickerRangeBody
- **Category:** `components/date_picker/body/month`
- **Description:** Mekari Mobile Kit: Month Date Range Picker <br/> This component will show all visible months in the following year <br/> User able to select month range inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `dateRange`, `labelStyle`, `cellStyle`, `events`, `onDateRangeSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4103-37846&t=m1pSRzXYXfjLCH2X-4

### MpMonthDatePickerRangeSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Range Picker - Month - Sheet <br/> This template will show all visible months in the following year in a sheet <br/> User able to select month range inside this sheet <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `dateRange`, `menuStyle`, `cellStyle`, `events`, `titleLabel`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4103-37846&t=m1pSRzXYXfjLCH2X-4

### MpMonthDatePickerSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker - Month - Sheet <br/> This template will show all visible months in the following year in a sheet <br/> User able to select month inside this sheet <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `menuStyle`, `cellStyle`, `events`, `titleLabel`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30987&t=ARnxQ2jFK0WP3Ih7-4

### MpMultiUpload
- **Category:** `components/upload`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Upload (Variant: Multi Upload)
- **Key params:** `data`, `label`, `caption`, `error`, `dropzoneIcon`, `dropzoneLabel`, `deleteIcon`, `deleteIconPadding`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=7014-59155

### MpMultipleLineBottomSheetContent
- **Category:** `components/bottom_sheet`
- **Description:** Mekari Mobile Kit - Bottomsheet - Variant: Multiple Line
- **Key params:** `title`, `labelButton`, `content`, `onTapClose`, `onTapButton`, `actions`, `actionSpacing`, `semantics`

### MpOutdentToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Decrease text indentation level in the text editor.
- **Key params:** `controller`, `tooltip`, `style`, `semantics`
- **Variants:** `MpOutdentToolbarButton.basic()`

### MpOverlineBottomSheetContent
- **Category:** `components/bottom_sheet`
- **Description:** Mekari Mobile Kit - Bottomsheet - Variant: Overline
- **Key params:** `title`, `labelButton`, `content`, `onTapClose`, `onTapButton`, `actions`, `actionSpacing`, `semantics`

### MpOverlineListTileXContent
- **Category:** `components/list_tile_x`
- **Key params:** `label`, `caption`, `labelStyle`, `captionStyle`, `overflow`, `textAlign`

### MpPageControl
- **Category:** `components/page_control`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Page Control.
- **Key params:** `length`, `onTap`, `activeColor`, `inactiveColor`, `height`, `content`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=1080-21107&mode=design&t=tvaCXuWAZslTRP27-0

### MpPageControlIndicator
- **Category:** `components/page_control`
- **Description:** A circular indicator widget that mainly used inside the [MpPageController]
- **Key params:** `index`, `isActive`, `onTap`, `indicatorSize`, `activeColor`, `inactiveColor`, `semantics`

### MpPageControlSlider
- **Category:** `components/page_control`
- **Description:** Mekari Mobile Kit - Page Control Slider.
- **Key params:** `content`, `scrollController`, `activeColor`, `inactiveColor`, `contentBuilder`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=1080%3A21106&mode=design&t=mHIVS3Gd7Jx2lLB0-1

### MpPageControlSliderIndicator
- **Category:** `components/page_control`
- **Key params:** `activeColor`, `inactiveColor`

### MpPhoneTextField
- **Category:** `components/phone_text_field`
- **Description:** Mekari Mobile Kit - Phone Textfield.
- **Key params:** `controller`, `focusNode`, `hint`, `error`, `helper`, `validator`, `onFocused`, `onChanged`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=86-2334&mode=design&t=7wbHsuCptahyue9P-0

### MpResetFormatToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Reset/clear all formatting from the current selection or line.
- **Key params:** `controller`, `tooltip`, `style`, `semantics`
- **Variants:** `MpResetFormatToolbarButton.basic()`

### MpScrollableDatePickerBody
- **Category:** `components/date_picker/body/scrollable`
- **Description:** Mekari Mobile Kit: Date Picker Scrollable Picker <br/> This component will show scrollable date picker <br/> User able to scroll and select date inside this view <br/>
- **Key params:** `firstDate`, `lastDate`, `selectedDate`, `itemExtent`, `onDateChanged`, `locale`, `semantics`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17503-8345&t=Pg2AMtKHlvhNuuIK-4

### MpScrollableDatePickerBodyView
- **Category:** `components/date_picker/body/scrollable`
- **Description:** Mekari Mobile Kit: Date Picker Scrollable View <br/> This component will show a vertical scrollable view <br/> User able to scroll values in this view <br/>
- **Key params:** `itemExtent`, `itemCount`, `itemBuilder`, `onControllerCreated`, `onSelectedItemChanged`, `semantics`, `maxHeight`, `itemExtent`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17503-8345&t=Pg2AMtKHlvhNuuIK-4

### MpScrollableDatePickerRangeBody
- **Category:** `components/date_picker/body/scrollable`
- **Description:** Mekari Mobile Kit: Scrollable Date Range Picker <br/> This component will show scrollable range date picker <br/> User able to scroll and select date range inside this view <br/>
- **Key params:** `firstDate`, `lastDate`, `dateRange`, `itemExtent`, `onDateRangeSelected`, `stringLibrary`, `locale`, `semantics`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17497-6849&t=Pg2AMtKHlvhNuuIK-4

### MpScrollableDatePickerRangeSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Range Picker - Scrollable - Sheet <br/> This component will show scrollable range date picker <br/> User able to scroll and select date range inside this view <br/>
- **Key params:** `firstDate`, `lastDate`, `dateRange`, `itemExtent`, `titleLabel`, `onClearButtonPressed`, `onSaveButtonPressed`, `stringLibrary`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17497-6849&t=Pg2AMtKHlvhNuuIK-4

### MpScrollableDatePickerSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker - Scrollable - Sheet <br/> This component will show scrollable date picker <br/> User able to scroll and select date inside this view <br/>
- **Key params:** `firstDate`, `lastDate`, `selectedDate`, `itemExtent`, `titleLabel`, `onClearButtonPressed`, `onSaveButtonPressed`, `stringLibrary`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17503-8345&t=Pg2AMtKHlvhNuuIK-4

### MpSearch
- **Category:** `components/search`
- **Description:** Mekari Mobile Kit - Search.
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=953%3A20829&t=pCVjH8TeC65kNarf-4

### MpSegmentedControl
- **Category:** `components/segmented_control`
- **Description:** ```
- **Key params:** `items`, `initialSelectedItem`, `tabController`, `controller`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=3113%3A16047&mode=design&t=0ovRDMW7Xr35mcNB-1

### MpSingleFilter
- **Category:** `components/filter/single`
- **Description:** Mekari Mobile Kit - Single Selection Filter A single selection filter widget that allows users to select one option from a list of available choices.
- **Key params:** `tags`, `selectedIndex`, `selectedStyle`, `unselectedStyle`, `onTapTag`, `backgroundColor`, `padding`, `spacing`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17733-5629&t=Mh1LR4y5qxayQyyP-4

### MpSingleListTileXContent
- **Category:** `components/list_tile_x`
- **Key params:** `label`, `style`, `overflow`, `textAlign`

### MpSlider
- **Category:** `components/slider`
- **Description:** Mekari Mobile Kit - Slider
- **Key params:** `title`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18084-55630&t=fgXbXl4CZVH4dcbK-0

### MpSliderRange
- **Category:** `components/slider`
- **Description:** Mekari Mobile Kit - Slider
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18084-55630&t=fgXbXl4CZVH4dcbK-0

### MpStories
- **Category:** `components/stories`
- **Description:** Mekari Mobile Kit - Stories
- **Key params:** `controller`, `onStart`, `onStop`, `onResume`, `onPause`, `onIndexChange`, `valueColor`, `backgroundColor`
- **Variants:** `MpStories.white()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=13919-13208&mode=design&t=2po2iJqfpiBg7bfg-0

### MpTabs
- **Category:** `components/tabs`
- **Description:** Mekari Mobile Kit Tabs.
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=95%3A3262&t=3PKxxhRsp4nKFlSh-0

### MpTabsChips
- **Category:** `components/tabs`
- **Description:** Mekari Mobile Kit Tabs.
- **Key params:** `onTap`, `backgroundColor`, `activeColor`, `inActiveColor`, `activeBackgroundColor`, `activeIconCustomColor`, `inActiveIconCustomColor`, `height`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17359-9407&t=ERjFywuCf1J3DBGZ-0

### MpTabsMenu
- **Category:** `components/tabs`
- **Description:** Mekari Mobile Kit Tabs.
- **Key params:** `onTap`, `backgroundColor`, `itemBackgroundColor`, `itemForegroundColor`, `activeIconCustomColor`, `inActiveIconCustomColor`, `height`, `itemSpacing`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17359-9407&t=ERjFywuCf1J3DBGZ-0

### MpTextEditor
- **Category:** `components/text_editor`
- **Description:** Mekari Mobile Kit - Text Editor
- **Key params:** `controller`, `style`, `mentions`, `onTapLink`, `onAttachmentDelete`, `onAttachmentDownload`, `toolbarBuilder`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5225-43924

### MpTextEditorAttachment
- **Category:** `components/text_editor`
- **Description:** This widget is a part of [MpTextEditor]. This widget show a list of images and files included to the text editor's document. This widget requires conteroller to show and remove images and files
- **Key params:** `controller`, `style`, `onTapDelete`, `onTapDownload`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5225-43924

### MpTextEditorContent
- **Category:** `components/text_editor`
- **Description:** This widget is a part of [MpTextEditor]. This widget placed at the center of text editor and used to update [MpTextEditorData.content].
- **Key params:** `controller`, `scrollController`, `focusNode`, `style`, `onLaunchUrl`, `semantics`
- **Variants:** `MpTextEditorContent.reader()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5225-43924

### MpTextEditorHeader
- **Category:** `components/text_editor`
- **Description:** This widget is a part of [MpTextEditor]. This widget placed at the top of the text editor.
- **Key params:** `controller`, `focusNode`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5225-43924

### MpTextEditorImagePreview
- **Category:** `components/text_editor`
- **Key params:** `attachment`, `onTapDelete`, `onTapDownload`, `backgroundColor`

### MpThumbnail
- **Category:** `components/thumbnail`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Thumbnail
- **Key params:** `path`, `size`, `radius`, `deleteIcon`, `deleteIconPadding`, `borderColor`, `onTapDelete`, `onTapThumbnail`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=7048-60414&mode=design&t=ERvQvSYg3uboxKst-4

### MpTimePickerBottomSheetContent
- **Category:** `components/time_picker`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - TimePicker To call the time picker inside bottomsheet, preferably use [MpTimePicker] instead.
- **Key params:** `onTapButton`, `onTapButtonRange`, `is12HourFormat`, `hoursLimit`, `minutesLimit`, `secondsLimit`, `initialHour`, `initialMinute`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5257-47630&mode=design&t=47dkyq9n3kUAnBSK-4

### MpTimePickerDuration
- **Category:** `components/time_picker`
- **Description:** Mekari Mobile Kit - TimePicker (Variant: Duration)
- **Key params:** `hoursLimit`, `minutesLimit`, `secondsLimit`, `backgroundColor`, `onTimeChanged`, `semantics`, `strings`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5257-47630&mode=design&t=47dkyq9n3kUAnBSK-4

### MpTimePickerField
- **Category:** `components/time_picker_field`
- **Description:** Mekari Mobile Kit - Time Picker Field.
- **Key params:** `controller`, `focusNode`, `label`, `hint`, `helper`, `validator`, `onChanged`, `padding`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17562-11823&t=HH7hDyVXTVWlgKEz-4

### MpTimePickerSpinner
- **Category:** `components/time_picker`
- **Description:** Spinner for hours, minutes, and seconds
- **Key params:** `controller`, `list`, `itemHeight`, `selectedIndex`, `onUpdateSelectedIndex`, `semantics`, `controller`, `itemHeight`

### MpTimePickerTime
- **Category:** `components/time_picker`
- **Description:** Mekari Mobile Kit - TimePicker (Variant: Time)
- **Key params:** `hoursLimit`, `minutesLimit`, `backgroundColor`, `onTimeChanged`, `semantics`, `strings`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17562-11783

### MpTimePickerTimeRange
- **Category:** `components/time_picker`
- **Description:** Mekari Mobile Kit - TimePicker (Variant: Time Range)
- **Key params:** `hoursLimit`, `minutesLimit`, `backgroundColor`, `onTimeRangeChanged`, `semantics`, `strings`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17562-11819&t=OJADDrCyLjcjLm9g-4

### MpTimePickerTypeSpinner
- **Category:** `components/time_picker`
- **Description:** Spinner for AM/PM
- **Key params:** `controller`, `itemHeight`, `selectedIndex`, `onUpdateSelectedIndex`, `semantics`, `strings`, `itemHeight`

### MpTimeline
- **Category:** `components/timeline`
- **Description:** Mekari Pixel - Timeline
- **Key params:** `indicator`, `label`, `preposition`, `username`, `date`, `desc`, `attachmentData`, `customContent`
- **Variants:** `MpTimeline.informative()`, `MpTimeline.success()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5343-46805&mode=design&t=COdbyxlFRHGuavvx-4

### MpTimelineAttachment
- **Category:** `components/timeline/attachment`
- **Description:** A attachment widget for Timeline widget
- **Key params:** `attachmentData`, `semantics`

### MpTimelineIndicator
- **Category:** `components/timeline/indicator`
- **Key params:** `icon`, `iconCollapse`, `onTapIcon`, `semantics`
- **Variants:** `MpTimelineIndicator.informative()`, `MpTimelineIndicator.success()`, `MpTimelineIndicator.negative()`, `MpTimelineIndicator.neutral()`, `MpTimelineIndicator.notice()`, `MpTimelineIndicator.accordion()`, `MpTimelineIndicator.cancelled()`

### MpTimelineIndicatorAccordionIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorCancelledIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorInformativeIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorNegativeIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorNeutralIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorNoticeIcon
- **Category:** `components/timeline/indicator`

### MpTimelineIndicatorSuccessIcon
- **Category:** `components/timeline/indicator`

### MpTimelineLog
- **Category:** `components/timeline/log`
- **Description:** A timeline log widget for Timeline widget
- **Key params:** `title`, `description`, `titleStyle`, `descriptionStyle`

### MpToast
- **Category:** `components/toast`
- **Description:** Mekari Pixel - Toast
- **Key params:** `message`, `icon`, `emoji`, `iconAnimation`, `direction`, `style`, `semantics`
- **Variants:** `MpToast.done()`, `MpToast.info()`, `MpToast.error()`, `MpToast.warning()`, `MpToast.greetings()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=279%3A3928&t=hajI1xdm3KpgcanQ-0

### MpToastIcon
- **Category:** `components/toast`
- **Description:** Display icon on top of the toast
- **Key params:** `icon`, `color`, `size`, `animation`

### MpToggleBottomSheetContent
- **Category:** `components/bottom_sheet`
- **Description:** Mekari Mobile Kit - Bottomsheet - Variant: Toggle
- **Key params:** `title`, `labelButton`, `content`, `style`, `onTapItem`, `onTapClose`, `onTapButton`, `actions`

### MpToggleToolbarButton
- **Category:** `components/text_editor/toolbar_button`
- **Description:** Trigger an action from tapping a button.
- **Key params:** `controller`, `attribute`, `icon`, `tooltip`, `style`, `onPressed`, `semantics`
- **Variants:** `MpToggleToolbarButton.bold()`, `MpToggleToolbarButton.italic()`, `MpToggleToolbarButton.underline()`, `MpToggleToolbarButton.strikethrough()`, `MpToggleToolbarButton.listBullet()`, `MpToggleToolbarButton.listNumber()`, `MpToggleToolbarButton.blockQuote()`

### MpTripleListTileXContent
- **Category:** `components/list_tile_x`
- **Key params:** `label`, `caption`, `description`, `labelStyle`, `captionStyle`, `descriptionStyle`, `overflow`, `textAlign`

### MpUpload
- **Category:** `components/upload`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Upload
- **Key params:** `data`, `label`, `caption`, `error`, `dropzoneIcon`, `dropzoneLabel`, `deleteIcon`, `deleteIconPadding`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=7014-59155

### MpUploadAttachment
- **Category:** `components/upload/attachment`
- **Key params:** `data`, `size`, `radius`, `icon`, `label`, `deleteIcon`, `deleteIconPadding`, `dropzoneStyle`

### MpUploadDropzone
- **Category:** `components/upload/dropzone`
- **Key params:** `icon`, `label`, `progress`, `onTap`, `onTapCancel`, `cancelIcon`, `style`, `semantics`

### MpUploadLabel
- **Category:** `components/upload`
- **Description:** Mekari Mobile Kit - Upload (Part: Label)
- **Key params:** `text`, `textStyle`, `text`, `text`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=7014-59155

### MpUploadListTile
- **Category:** `components/upload`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Upload (Variant: List Tile)
- **Key params:** `label`, `caption`, `data`, `padding`, `onTap`, `onTapUpload`, `onTapRefresh`, `onTapDelete`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=7014-59155

### MpVideoPlayer
- **Category:** `components/video_player`
- **Key params:** `file`, `videoUrl`, `height`, `width`, `semantics`

### MpYearDatePickerBody
- **Category:** `components/date_picker/body/year`
- **Description:** Mekari Mobile Kit: Date Picker - Year <br/> This component will show all visible years <br/> User able to select year inside this view <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `labelStyle`, `cellStyle`, `events`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30993&t=crHQWqZtF43eji1F-4

### MpYearDatePickerBodyView
- **Category:** `components/date_picker/body/year`
- **Description:** Mekari Mobile Kit: Date Picker - Year <br/> This component will show all visible years <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `dateRange`, `cellStyle`, `events`, `onDateSelected`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30993&t=crHQWqZtF43eji1F-4

### MpYearDatePickerSheet
- **Category:** `components/date_picker/sheet`
- **Description:** Mekari Mobile Kit: Date Picker - Year - Sheet <br/> This template will show all available years in a sheet <br/> User able to select year inside this sheet <br/>
- **Key params:** `date`, `firstDate`, `lastDate`, `selectedDate`, `menuStyle`, `cellStyle`, `events`, `titleLabel`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=4095-30993&t=crHQWqZtF43eji1F-4

---

## Pages

### MpCalendar
- **Category:** `pages/calendar`
- **Description:** Mekari Pixel - Calendar
- **Key params:** `initialDate`, `locale`, `backgroundColor`, `onFocusDateChanged`, `onDateSelected`, `itemBuilder`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18167-65383

### MpCalendarBody
- **Category:** `pages/calendar/bodies`
- **Key params:** `selectedDate`, `focusedDate`, `locale`, `onDaySelected`, `onFormatChanged`, `onPageChanged`, `strings`, `itemBuilder`

### MpCalendarBodyItem
- **Category:** `pages/calendar/bodies`
- **Key params:** `label`, `items`, `onTapItem`

### MpCalendarBodyList
- **Category:** `pages/calendar/bodies`
- **Key params:** `date`, `strings`, `locale`, `itemBuilder`

### MpCalendarEvent
- **Category:** `pages/calendar`
- **Key params:** `data`, `onTap`, `backgroundColor`, `iconColor`, `labelColor`, `captionColor`

### MpCalendarListBody
- **Category:** `pages/calendar/bodies`
- **Key params:** `locale`, `strings`, `itemBuilder`

### MpCalendarListBodySection
- **Category:** `pages/calendar/bodies`
- **Key params:** `date`, `data`, `locale`, `strings`, `itemBuilder`

### MpCalendarTable
- **Category:** `pages/calendar/bodies`
- **Key params:** `selectedDate`, `focusedDate`, `locale`, `onDaySelected`, `onFormatChanged`, `onPageChanged`

### MpCameraScreen
- **Category:** `pages/camera`
- **Key params:** `captureWith`, `availableCaptureMode`, `onCameraError`, `guideView`, `onTapClose`, `imageAspectRatio`, `semantics`

### MpFeedbackDetailOptionGroup
- **Category:** `pages/feedback/widgets`
- **Description:** Mekari Mobile Kit - Feedback Detail Option Group
- **Key params:** `activeOptionsColor`, `inactiveOptionsColor`, `activeOptionsBorderColor`, `inactiveOptionsBorderColor`, `onSelectedOptionsChanged`, `stringLibrary`, `locale`, `parentSemantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11154-19124&mode=design&t=fxwY8WkW2dsIEABB-4

### MpFeedbackDetailSheet
- **Category:** `pages/feedback/sheets`
- **Description:** Mekari Mobile Kit - Feedback Detail Sheet
- **Key params:** `activeOptionsColor`, `inactiveOptionsColor`, `activeOptionsBorderColor`, `inactiveOptionsBorderColor`, `feedbackTextStyle`, `onDetailSubmitted`, `stringLibrary`, `locale`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11175-1273&mode=design&t=fxwY8WkW2dsIEABB-4

### MpFeedbackRatingSheet
- **Category:** `pages/feedback/sheets`
- **Description:** Mekari Mobile Kit - Feedback Rating Sheet <br/> Has 2 variations: [MpFeedbackRatingSheet.csat] and [MpFeedbackRatingSheet.nps]
- **Variants:** `MpFeedbackRatingSheet.csat()`, `MpFeedbackRatingSheet.nps()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11154-19178&mode=design&t=fxwY8WkW2dsIEABB-4

### MpFeedbackRatingSheetSelection
- **Category:** `pages/feedback/widgets`
- **Description:** Mekari Mobile Kit - Feedback Rating Selection
- **Key params:** `activeOptionsColor`, `inactiveOptionsColor`, `onOptionSelected`, `parentSemantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11154-19026&mode=design&t=fxwY8WkW2dsIEABB-4

### MpFeedbackRatingSheetSlider
- **Category:** `pages/feedback/widgets`
- **Description:** Mekari Mobile Kit - Feedback Rating Slider
- **Key params:** `activeTrackColor`, `inactiveTrackColor`, `activeTextColor`, `inactiveTextColor`, `borderRadius`, `onValueChanged`, `onValueStart`, `onValueEnd`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11175-1696&mode=design&t=fxwY8WkW2dsIEABB-4

### MpFeedbackStoreSheet
- **Category:** `pages/feedback/sheets`
- **Description:** Mekari Mobile Kit - Feedback Store Sheet
- **Key params:** `appName`, `playStoreUrl`, `appStoreUrl`, `fallbackUrl`, `stringLibrary`, `locale`, `onTapLater`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=11175-1425&mode=design&t=fxwY8WkW2dsIEABB-4

### MpLaunchScreen
- **Category:** `pages/launch_screen`
- **Description:** Mekari Mobile Kit - Launch Screen.
- **Key params:** `nextRoute`, `builder`, `color`, `progress`, `onAnimationFinished`, `semantics`, `nextRoute`, `progress`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5973%3A56054&mode=design&t=HA35ty2rlKN988PI-1

### MpLaunchScreenProgress
- **Category:** `pages/launch_screen`
- **Key params:** `progress`, `onFinished`, `semantics`

### MpLogoAnimation
- **Category:** `pages/launch_screen`
- **Key params:** `logoAssets`, `textAssets`, `animationType`, `onAnimationFinished`, `key`, `duration`

### MpOtpField
- **Category:** `pages/otp_pin/otp`
- **Description:** Used to show otp field
- **Key params:** `onOtpFilled`, `controller`, `semantics`

### MpOtpFieldCursor
- **Category:** `pages/otp_pin/otp`
- **Description:** Used by [MpOtpField] to show an animated cursor
- **Key params:** `width`, `color`

### MpOtpScreen
- **Category:** `pages/otp_pin/otp`
- **Description:** Mekari Mobile Kit - Otp Screen.
- **Key params:** `phoneNumber`, `otpTarget`, `onValidateOTP`, `onResendOTP`, `resendDuration`, `onOtpValidated`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=10070-17862&mode=design&t=qAYF5ixClkRNMQbQ-4

### MpPinKeyboard
- **Category:** `pages/otp_pin/pin`
- **Description:** Used to handling user interaction on filling the pin / validate biometrics
- **Key params:** `onKeyTap`, `biometricsIcon`, `semantics`

### MpPinScreen
- **Category:** `pages/otp_pin/pin`
- **Description:** Mekari Mobile Kit - Otp Screen.
- **Key params:** `onValidatePin`, `showBiometrics`, `onValidateBiometrics`, `onForgotPinTap`, `onValidated`, `onPinExhausted`, `actionType`, `limit`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=10070-23772&mode=design&t=qAYF5ixClkRNMQbQ-4

### MpProfileInfoSection
- **Category:** `pages/profile`
- **Description:** Mekari Mobile Kit: Profile - Info Section <br/> This template will display profile for user information <br/> Contains: fullname, avatar, additional info, etc <br/>
- **Key params:** `fullname`, `fullnameTextStyle`, `badge`, `additionalInfo`, `avatarUrl`, `avatarVariant`, `onAvatarVariantChanged`, `isLoading`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56881&mode=design&t=luIN3jn3XzVPseKD-0

### MpProfileMenuItem
- **Category:** `pages/profile`
- **Description:** Mekari Mobile Kit: Profile - Menu Item <br/> Derived from [MpListTileX], <br/> Add a new default config for loading <br/>
- **Key params:** `content`, `leading`, `actions`, `spacing`, `actionSpacing`, `actionMaxWidth`, `padding`, `onTap`
- **Variants:** `MpProfileMenuItem.loading()`, `MpProfileMenuItem.navigation()`, `MpProfileMenuItem.toggle()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56881&mode=design&t=luIN3jn3XzVPseKD-0

### MpProfileMenuSection
- **Category:** `pages/profile`
- **Description:** Mekari Mobile Kit: Profile - Menu Section <br/> This template will help to organize profile menu <br/>
- **Key params:** `label`, `items`, `backgroundColor`, `isLoading`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56881&mode=design&t=luIN3jn3XzVPseKD-0

### MpProfilePage
- **Category:** `pages/profile`
- **Description:** Mekari Mobile Kit: Profile - Page <br/> This template will display and organize Profile <br/> Contains: info section, menu section, and an app version <br/>
- **Key params:** `profileInfo`, `menus`, `banner`, `appVersion`, `appVersionStyle`, `scrollController`, `backgroundColor`, `statusBarColor`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56881&mode=design&t=luIN3jn3XzVPseKD-0

### MpReportProblemPage
- **Category:** `pages/report_problem`
- **Description:** Mekari Mobile Kit: Report Problem - Page <br/> This template will be used to report problems <br/>
- **Key params:** `title`, `url`, `onSubmit`, `backgroundColor`, `semantics`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18191-87736

### MpReportProblemSubmissionPage
- **Category:** `pages/report_problem`
- **Description:** Mekari Mobile Kit: Report Problem - Page <br/> This template will be used to report problems <br/>
- **Key params:** `onClickGallery`, `onClickCamera`, `onSubmit`, `subHeader`, `scrollController`, `backgroundColor`, `statusBarColor`, `systemUiOverlayStyle`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18191-87736

### MpServerFeedbackBottomSheet
- **Category:** `pages/server_feedback`
- **Description:** @Author: Agung Nursatria (agung.nursatria@mekari.com)
- **Key params:** `data`, `style`, `semantics`

### MpServerFeedbackPage
- **Category:** `pages/server_feedback`
- **Description:** @Author: Agung Nursatria (agung.nursatria@mekari.com)
- **Key params:** `data`, `style`, `semantics`

### MpSignOut
- **Category:** `pages/sign_out`
- **Description:** Mekari Mobile Kit - Sign Out
- **Key params:** `title`, `body`, `onSignIn`, `onSignOut`, `signInButtonText`, `signOutButtonText`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56887&mode=design&t=nWDcLiL9cMPsLNhj-0

---

## Templates

### MpAccordion
- **Category:** `templates/accordion`
- **Description:** Mekari Mobile Kit - Accordion
- **Key params:** `title`, `content`, `leading`, `actions`, `actionSpacing`, `titleStyle`, `caption`, `captionStyle`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=525-6782&mode=design&t=cEYidMURVunqpGZf-0

### MpActionGroup
- **Category:** `templates/action_group`
- **Description:** Mekari Pixel - Action Group A group of action (mostly buttons) that are related to each other.
- **Key params:** `actions`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=1162%3A21700&t=ycZkZqNp4OSmeRHD-0

### MpAppLock
- **Category:** `templates/app_lock`
- **Description:** Mekari Pixel - App Lock
- **Key params:** `hideBuilder`, `lockBuilder`, `semantics`, `child`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18059-53848&t=Za1XapCYV25k2MEl-0

### MpAppLockBlur
- **Category:** `templates/app_lock`

### MpAvatarVariation
- **Category:** `templates/avatar_variation`
- **Description:** Mekari Mobile Kit - Avatar - Part: Variation Mainly used on [MpAvatar] to show badge at the corner of the widget.
- **Key params:** `variation`, `child`, `position`, `onTapVariation`, `semantics`

### MpAvatarVariationIcon
- **Category:** `templates/avatar_variation`
- **Description:** Mekari Mobile Kit - Avatar - Part: Variation
- **Key params:** `id`, `icon`, `iconColor`, `backgroundColor`, `borderColor`, `label`
- **Variants:** `MpAvatarVariationIcon.available()`, `MpAvatarVariationIcon.away()`, `MpAvatarVariationIcon.busy()`, `MpAvatarVariationIcon.offline()`, `MpAvatarVariationIcon.open()`

### MpAvatarVariationPositioned
- **Category:** `templates/avatar_variation`
- **Key params:** `position`, `child`

### MpBasicLayout
- **Category:** `templates/basic_layout`
- **Key params:** `appBar`, `stage`, `bottomNavigationBar`, `stagePosition`, `backgroundColor`, `contentStyle`, `scrollController`, `scrollPhysics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=44-965&mode=design&t=xGQkQxtKsKverfZm-0

### MpBottomSheetContent
- **Category:** `templates/bottom_sheet`
- **Description:** Mekari Mobile Kit - Dialog - Content
- **Key params:** `body`, `header`, `footer`, `handler`, `backgroundColor`, `headerBackgroundColor`, `bodyPadding`, `scrollPhysics`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17806-4384

### MpBottomSheetHandler
- **Category:** `templates/bottom_sheet`
- **Description:** Mekari Mobile Kit - Dialog - Handler
- **Key params:** `color`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17806-4384

### MpBottomSheetHeader
- **Category:** `templates/bottom_sheet`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Dialog - Header
- **Key params:** `title`, `titleTextStyle`, `titleColor`, `leading`, `iconColor`, `actions`, `onTapClose`, `padding`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17806-4384

### MpCheckboxHeaderListTileX
- **Category:** `templates/checkbox_list_tile_x`
- **Description:** Mekari Mobile Kit - Checkbox - Variant: Basic, Icon Left, Avatar An updated version of the [MpRadioButtonListTile]
- **Key params:** `content`, `leading`, `checkboxStyle`, `onChanged`, `backgroundColor`, `iconColor`, `padding`, `spacing`
- **Variants:** `MpCheckboxHeaderListTileX.single()`, `MpCheckboxHeaderListTileX.overline()`, `MpCheckboxHeaderListTileX.double()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5308&t=c8IIoGc1ZdE8vXIF-0

### MpCheckboxListTileX
- **Category:** `templates/checkbox_list_tile_x`
- **Description:** Mekari Mobile Kit - Checkbox - Variant: Basic, Icon Left, Avatar An updated version of the [MpRadioButtonListTile]
- **Key params:** `content`, `leading`, `checkboxStyle`, `onChanged`, `backgroundColor`, `iconColor`, `padding`, `spacing`
- **Variants:** `MpCheckboxListTileX.single()`, `MpCheckboxListTileX.overline()`, `MpCheckboxListTileX.double()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=445%3A5308&t=c8IIoGc1ZdE8vXIF-0

### MpCoachmark
- **Category:** `templates/coachmark`
- **Description:** Mekari Mobile Kit - Coachmark
- **Key params:** `child`, `coachmark`, `onSaveShownState`, `onReadShownState`, `onReadyStart`, `onCandidateStart`, `onFinished`, `showCounter`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=8672%3A12033&mode=design&t=SZd6ttwmNp8l0OU1-1

### MpCoachmarkAnimation
- **Category:** `templates/coachmark/utils`
- **Description:** Widget to animate [MpCoachmark] stuff
- **Key params:** `child`

### MpCoachmarkContainer
- **Category:** `templates/coachmark/widgets`
- **Key params:** `title`, `description`, `icon`, `semantics`

### MpCoachmarkTooltip
- **Category:** `templates/coachmark/widgets`
- **Key params:** `title`, `description`, `parentPosition`, `position`, `length`, `doneLabel`, `showCounter`, `semantics`

### MpCoachmarkWrapper
- **Category:** `templates/coachmark/widgets`
- **Description:** Used to wrap widget to be a part of [MpCoachmark]
- **Key params:** `name`, `child`, `title`, `description`, `coachmarkChild`, `icon`

### MpContent
- **Category:** `templates/content`
- **Key params:** `child`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=44-965&mode=design&t=xGQkQxtKsKverfZm-0

### MpDialogContent
- **Category:** `templates/dialog`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Dialog - Content
- **Key params:** `header`, `body`, `bodyTextStyle`, `bodyPadding`, `bodyScrollController`, `footer`, `backgroundColor`, `borderRadius`
- **Variants:** `MpDialogContent.basic()`, `MpDialogContent.basicSide()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17406-4608

### MpDialogHeader
- **Category:** `templates/dialog`
- **Description:** Mekari Mobile Kit - Dialog - Header
- **Key params:** `title`, `textStyle`, `iconColor`, `backgroundColor`, `padding`, `semantics`
- **Variants:** `MpDialogHeader.basic()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17406-4608

### MpDialogSideFooter
- **Category:** `templates/dialog`
- **Description:** Mekari Mobile Kit - Dialog - Footer
- **Key params:** `actions`, `borderColor`, `semantics`
- **Variants:** `MpDialogSideFooter.basic()`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=17406-4608

### MpFloatingActionButtonStack
- **Category:** `templates/floating_action_button`
- **Description:** This widget is a helper to stack [MpFloatingActionButton] on top of another widget. Used when we can't use [Scaffold.floatingActionButton].
- **Key params:** `floatingActionButton`, `child`, `scrollController`, `onScroll`, `child`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=17587-13389&t=AvL1D1iHweZxKwW9-0

### MpGuideTourContent
- **Category:** `templates/guide_tour`
- **Key params:** `backgroundColor`, `header`, `content`, `illustration`, `actions`, `semantics`

### MpGuideTourHeader
- **Category:** `templates/guide_tour`
- **Description:** The header properties of [MpGuideTour].
- **Key params:** `icon`, `label`, `labelStyle`, `indicator`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56880&mode=design&t=Ab1THGR4B1QXjmf5-0

### MpHeaderListTileX
- **Category:** `templates/list_tile_x/header`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - List Tile (Variant: Basic, Icon Left, Avatar) An updated design version of [MpHeaderListTile]
- **Key params:** `content`, `leading`, `trailing`, `actions`, `spacing`, `actionSpacing`, `actionMaxWidth`, `padding`
- **Variants:** `MpHeaderListTileX.single()`, `MpHeaderListTileX.double()`, `MpHeaderListTileX.sub()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=90%3A2543&t=B6BEQozI82pK7WdO-0

### MpHorizontalBanner
- **Category:** `templates/horizontal_banner`
- **Description:** Mekari Pixel Horizontal Banner Widget to create banner that can be clicked with pop out illustration
- **Key params:** `onPressed`, `image`, `gradient`, `titleWidget`, `titleLabel`, `titleBoldLabel`, `ctaLabel`, `textColor`
- **Figma:** https://www.figma.com/design/djepS92jOSLv9ayVBIcH4M/Mobile-Pixel-2.4?node-id=18179-76385&t=f7hmR4XI7DC3azVP-0

### MpListTileX
- **Category:** `templates/list_tile_x`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - List Tile (Variant: Basic, Icon Left, Avatar) An updated design version of [MpListTile] and [MpContentListTile]
- **Key params:** `content`, `leading`, `trailing`, `actions`, `spacing`, `actionSpacing`, `actionMaxWidth`, `padding`
- **Variants:** `MpListTileX.single()`, `MpListTileX.double()`, `MpListTileX.triple()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=90%3A2543&t=B6BEQozI82pK7WdO-0

### MpListTileXActionWrapper
- **Category:** `templates/list_tile_x/widgets`
- **Key params:** `actions`, `spacing`, `maxWidth`, `actions`, `spacing`, `maxWidth`

### MpMenuBadge
- **Category:** `templates/menu_badge`
- **Description:** Positioned badge on top of menu (child)
- **Key params:** `badge`, `child`, `position`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=95%3A2769&t=txtn7MyTRAzcR9ZC-0

### MpMenuBadgePositioned
- **Category:** `templates/menu_badge`
- **Description:** A widget to wrap a badge and any widget, And set the badge to a desired position
- **Key params:** `position`, `child`, `semantics`

### MpProgressIndicator
- **Category:** `templates/progress_indicator`
- **Description:** ```
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=10000-1177&mode=design&t=CyqYd8XeCXbecmFL-0

### MpPullToRefresh
- **Category:** `templates/pull_to_refresh`
- **Description:** Mekari Mobile Kit - Pull to Refresh
- **Key params:** `controller`, `child`, `onRefresh`, `scrollController`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=5989-56884&mode=design&t=hzP489xr80YeZvqH-0

### MpStepper
- **Category:** `templates/stepper`
- **Description:** ```
- **Key params:** `controller`, `style`, `semantics`
- **Variants:** `MpStepper.number()`, `MpStepper.singleBar()`, `MpStepper.multipleBar()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=12643-5962&mode=design&t=9QoPUblW1lusDxih-0

### MpStepperBar
- **Category:** `templates/stepper`
- **Description:** Mekari Mobile Kit - MpStepper - Part: Bar.
- **Key params:** `steps`, `position`, `labels`, `type`, `style`, `semantics`
- **Variants:** `MpStepperBar.single()`, `MpStepperBar.multiple()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=12643-5962&mode=design&t=9QoPUblW1lusDxih-0

### MpStepperNumber
- **Category:** `templates/stepper`
- **Description:** Mekari Mobile Kit - MpStepper - Part: Number.
- **Key params:** `steps`, `position`, `padding`, `labels`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=12643-5962&mode=design&t=9QoPUblW1lusDxih-0

### MpStepperNumberIndicator
- **Category:** `templates/stepper`
- **Description:** Mekari Mobile Kit - MpStepper - Part: Number Indicator.
- **Key params:** `number`, `type`, `position`, `label`, `style`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?type=design&node-id=12643-5962&mode=design&t=9QoPUblW1lusDxih-0

### MpStickyButton
- **Category:** `templates/sticky_button`
- **Description:** A convenience widget that wrap Button widget inside elevatedcontainer.
- **Key params:** `button`, `backgroundColor`, `isAndroid`, `semantics`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(WIP)?node-id=31%3A633&t=hWde3rzGFr4eUnLJ-0

### MpToggleHeaderListTileX
- **Category:** `templates/toggle_list_tile_x`
- **Description:** Mekari Mobile Kit - Toogle - Header List Tile An updated version of the [MpToggleListTile] and [MpIconLeftToggleListTile]
- **Key params:** `content`, `leading`, `toggleStyle`, `size`, `onChanged`, `backgroundColor`, `iconColor`, `padding`
- **Variants:** `MpToggleHeaderListTileX.single()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=448%3A6576&t=nPrga1tGl9WiRGaY-0

### MpToggleListTileX
- **Category:** `templates/toggle_list_tile_x`
- **Description:** ---------------------------------------------------------------- Mekari Mobile Kit - Toogle - List Tile An updated version of the [MpToggleListTile] and [MpIconLeftToggleListTile]
- **Key params:** `content`, `leading`, `toggleStyle`, `size`, `onChanged`, `backgroundColor`, `iconColor`, `padding`
- **Variants:** `MpToggleListTileX.single()`, `MpToggleListTileX.double()`, `MpToggleListTileX.triple()`
- **Figma:** https://www.figma.com/file/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1-(In-test)?node-id=448%3A6576&t=nPrga1tGl9WiRGaY-0

### MpWalkthrough
- **Category:** `templates/walkthrough`
- **Description:** Mekari Mobile Kit - Walkthrough
- **Key params:** `productLogo`, `productName`, `pages`, `greeting`, `pageBuilder`, `onPageChanged`, `progressBarProperties`, `systemUiOverlayStyle`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5991-57434&t=lv01padf2kzSkYy4-4

### MpWalkthroughWebview
- **Category:** `templates/walkthrough`
- **Description:** Mekari Mobile Kit - Walkthrough Screen (Webview)
- **Key params:** `productName`, `walkthroughUrl`, `locale`
- **Figma:** https://www.figma.com/design/Lp6VSWJnP5wI4SdztB5H2f/Mobile-Kit-2.1?node-id=5998-56719&t=lv01padf2kzSkYy4-0
