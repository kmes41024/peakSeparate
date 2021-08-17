# 拉曼光譜重疊峰的分峰擬合

<img src="img/ui.png" alt="ui_demo" width="90%"/>

## 實作目的
* 使原始光譜曲線擬合
* 找到在重疊峰中可能包含的單峰

<img src="img/intro.png" alt="intro" width="90%"/>


## 實作流程
<br>
<img src="img/step.png" alt="step" width="90%"/>

## Step 1. 光譜前處理
* <b>將光譜高度 < 50的點設為0</b><br>
  ##### (下圖中的`藍色線段`為原始的光譜，`紅色線段`為處理後的光譜)
   <img src="img/preprocessing_1.png" alt="preprocessing_1" width="80%" height="70%"/>
* <b>切割光譜</b><br>
  * 從 0 開始到下一個 0 切一段

