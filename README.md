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
1. <b>將光譜高度 < 50的點設為0</b><br>
    ##### (下圖中的`藍色線段`為原始的光譜，`紅色線段`為處理後的光譜)
   <img src="img/preprocessing_1.png" alt="preprocessing_1" width="80%" height="70%"/>
2. <b>切割光譜</b><br>
    * 從 高度0 開始到下一個 高度0 切一段   (如下圖 `黃色框框` )<br>
    * 若切出來的峰最高點 <200 則忽略不算   (如下圖 `紅色框框` ) <br><br>
     <img src="img/preprocessing_2.png" alt="preprocessing_2" width="80%" height="60%"/>
  
## Step 2. 設置參數
  可調整參數：[ <b>強度</b> (amp)，<b>位置</b> (ctr)，<b>寬度</b> (wid) ]<br>
  * <b>強度影響：</b><br>
  經多次測試後，發現強度設置的大小對於最終結果並無太大的影響。<br>
  為了能使程式自動化，強度<b>一律設為0</b>。
    <br>
  
  * <b>寬度影響：</b>
 <img src="img/setParm_1.png" alt="setParm_1" width="70%" height="40%"/>
  
  * <b>參數設置：</b><br>
    <b>強度：</b> 0<br>
    <b>寬度：</b> 從 <b>10</b> 開始，若無法擬合 --> 寬度 + 2<br>
    <b>位置：</b> 從該峰的最高點往左右兩端，每隔一個寬度取一組參數。 取到x座標的高度等於0為止<br><br>
     <img src="img/setParm_2.png" alt="setParm_2" width="70%" height="40%"/>
      ##### ( 上圖中，當x座標為 786 和 816 時，高度 = 0，因此 peak = [0, 786, 5] 及 peak = [0, 816, 5] 不採用。 )

## Step 3. 曲線擬合
   利用高斯曲線擬合的方式，使原始光譜達到降噪的效果
   <img src="img/curve_fit.png" alt="curve_fit" width="70%" height="30%"/>
  
## Step 4. 分峰
 <img src="img/peak_separate.png" alt="peak_separate" width="70%" height="30%"/>
